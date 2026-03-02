#!/usr/bin/env python3
"""
企业微信客服群监控系统 - MVP版本
针对2个群的测试版本
"""

import sqlite3
import json
import yaml
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

class Database:
    """SQLite数据库管理"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """初始化数据表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 问题记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id TEXT PRIMARY KEY,
                group_id TEXT,
                group_name TEXT,
                customer_id TEXT,
                customer_name TEXT,
                content TEXT,
                issue_type TEXT DEFAULT '其他',
                priority TEXT DEFAULT '普通',
                created_at TIMESTAMP,
                first_response_at TIMESTAMP,
                resolved_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                handler TEXT,
                closure_confirmed BOOLEAN DEFAULT 0
            )
        ''')
        
        # 消息记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                issue_id TEXT,
                group_id TEXT,
                sender_type TEXT,
                sender_name TEXT,
                content TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        # 预警记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                issue_id TEXT,
                alert_type TEXT,
                sent_at TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_issue(self, issue: Dict):
        """添加新问题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO issues 
            (id, group_id, group_name, customer_id, customer_name, content, 
             issue_type, priority, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            issue['id'], issue['group_id'], issue['group_name'],
            issue['customer_id'], issue['customer_name'], issue['content'],
            issue.get('issue_type', '其他'), issue.get('priority', '普通'),
            issue['created_at'], 'pending'
        ))
        conn.commit()
        conn.close()
    
    def get_pending_issues(self) -> List[Dict]:
        """获取待处理问题"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM issues 
            WHERE status IN ('pending', 'processing')
            ORDER BY created_at ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_issue_response(self, issue_id: str, handler: str):
        """更新问题首次响应"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE issues 
            SET first_response_at = ?, status = 'processing', handler = ?
            WHERE id = ? AND first_response_at IS NULL
        ''', (datetime.now().isoformat(), handler, issue_id))
        conn.commit()
        conn.close()
    
    def resolve_issue(self, issue_id: str):
        """标记问题已解决"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE issues 
            SET resolved_at = ?, status = 'resolved'
            WHERE id = ?
        ''', (datetime.now().isoformat(), issue_id))
        conn.commit()
        conn.close()
    
    def get_daily_stats(self, date: str) -> Dict:
        """获取每日统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总问题数
        cursor.execute('''
            SELECT COUNT(*) FROM issues 
            WHERE DATE(created_at) = ?
        ''', (date,))
        total = cursor.fetchone()[0]
        
        # 已解决
        cursor.execute('''
            SELECT COUNT(*) FROM issues 
            WHERE DATE(created_at) = ? AND status IN ('resolved', 'closed')
        ''', (date,))
        resolved = cursor.fetchone()[0]
        
        # 平均响应时间
        cursor.execute('''
            SELECT AVG(
                (julianday(first_response_at) - julianday(created_at)) * 24 * 60
            ) FROM issues 
            WHERE DATE(created_at) = ? AND first_response_at IS NOT NULL
        ''', (date,))
        avg_response = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total': total,
            'resolved': resolved,
            'pending': total - resolved,
            'avg_response_minutes': round(avg_response, 1)
        }


class IssueAnalyzer:
    """问题识别与分类"""
    
    KEYWORDS = {
        '技术问题': ['报错', '失败', '无法', 'bug', '错误', '异常', '不能', '问题'],
        '服务请求': ['申请', '开通', '配置', '权限', '开通', '需要', '想要'],
        '投诉建议': ['不满', '投诉', '建议', '改进', '不好', '差'],
        '紧急故障': ['宕机', '崩溃', '不可用', '严重', '急', '紧急']
    }
    
    def classify(self, content: str) -> tuple:
        """分类问题类型和优先级"""
        content = content.lower()
        
        # 判断问题类型
        issue_type = '其他'
        for type_name, keywords in self.KEYWORDS.items():
            if any(kw in content for kw in keywords):
                issue_type = type_name
                break
        
        # 判断优先级
        priority = '普通'
        if any(kw in content for kw in self.KEYWORDS['紧急故障']):
            priority = '紧急'
        elif issue_type == '技术问题':
            priority = '高'
        
        return issue_type, priority
    
    def is_customer_question(self, content: str) -> bool:
        """判断是否是客户问题（而非闲聊）"""
        # 简单规则：包含问号或关键词
        question_keywords = ['?', '？', '怎么', '如何', '为什么', '请问', '求助']
        return any(kw in content for kw in question_keywords)


class AlertManager:
    """预警管理"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.warning_threshold = config['ALERT']['WARNING_THRESHOLD']
        self.urgent_threshold = config['ALERT']['URGENT_THRESHOLD']
    
    def check_alerts(self, db: Database) -> List[Dict]:
        """检查需要预警的问题"""
        pending_issues = db.get_pending_issues()
        alerts = []
        now = datetime.now()
        
        for issue in pending_issues:
            created_at = datetime.fromisoformat(issue['created_at'])
            elapsed_minutes = (now - created_at).total_seconds() / 60
            
            if elapsed_minutes >= self.urgent_threshold:
                alerts.append({
                    'issue': issue,
                    'level': 'urgent',
                    'message': f"🚨 紧急！问题超{self.urgent_threshold}分钟未响应"
                })
            elif elapsed_minutes >= self.warning_threshold:
                alerts.append({
                    'issue': issue,
                    'level': 'warning',
                    'message': f"⚠️ 问题超{self.warning_threshold}分钟未响应"
                })
        
        return alerts
    
    def send_alert(self, alert: Dict, webhook: str):
        """发送预警消息到企业微信群"""
        issue = alert['issue']
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"""{alert['message']}

**群名称：** {issue['group_name']}
**客户：** {issue['customer_name']}
**问题：** {issue['content'][:100]}...
**创建时间：** {issue['created_at']}
**已等待：** {self._format_duration(issue['created_at'])}

请尽快处理！"""
            }
        }
        
        try:
            response = requests.post(webhook, json=message, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"发送预警失败: {e}")
            return False
    
    def _format_duration(self, created_at: str) -> str:
        """格式化持续时间"""
        created = datetime.fromisoformat(created_at)
        elapsed = datetime.now() - created
        minutes = int(elapsed.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes}分钟"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}小时{mins}分钟"


class DailyReporter:
    """日报生成"""
    
    def __init__(self, db: Database, config: Dict):
        self.db = db
        self.config = config
    
    def generate_report(self, date: str = None) -> str:
        """生成日报"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        stats = self.db.get_daily_stats(date)
        
        report = f"""📅 客服群监控日报 - {date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 今日概览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 总问题数：{stats['total']}个
• 已解决：{stats['resolved']}个 ({self._percentage(stats['resolved'], stats['total'])})
• 待处理：{stats['pending']}个
• 平均首次响应时间：{stats['avg_response_minutes']}分钟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ 响应时间分布
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 30分钟内响应：{self._get_response_distribution(date, 30)}%
• 1小时内响应：{self._get_response_distribution(date, 60)}%
• 超1小时响应：{self._get_overtime_rate(date)}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 待跟进问题
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{self._get_pending_list()}

---
🤖 自动生成的客服监控日报
"""
        return report
    
    def _percentage(self, part: int, total: int) -> str:
        if total == 0:
            return "0%"
        return f"{round(part/total*100, 1)}%"
    
    def _get_response_distribution(self, date: str, minutes: int) -> str:
        # 简化版本，实际应该查询数据库
        return "--"
    
    def _get_overtime_rate(self, date: str) -> str:
        return "--"
    
    def _get_pending_list(self) -> str:
        pending = self.db.get_pending_issues()
        if not pending:
            return "✅ 无待处理问题"
        
        lines = []
        for i, issue in enumerate(pending[:5], 1):
            lines.append(f"{i}. [{issue['group_name']}] {issue['content'][:30]}...")
        
        if len(pending) > 5:
            lines.append(f"... 还有 {len(pending) - 5} 个问题")
        
        return "\n".join(lines)


class WeComCustomerService:
    """主控制器"""
    
    def __init__(self, config_path: str = "./config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.db = Database(self.config['STORAGE']['DB_PATH'])
        self.analyzer = IssueAnalyzer()
        self.alert_manager = AlertManager(self.config)
        self.reporter = DailyReporter(self.db, self.config)
    
    def simulate_customer_message(self, group_id: str, customer_name: str, content: str):
        """
        模拟接收客户消息（MVP版本，实际应该对接企业微信API）
        """
        # 判断是否是问题
        if not self.analyzer.is_customer_question(content):
            return None
        
        # 获取群信息
        group = self._get_group_info(group_id)
        
        # 分类问题
        issue_type, priority = self.analyzer.classify(content)
        
        # 创建问题记录
        issue_id = hashlib.md5(f"{group_id}:{customer_name}:{content}:{datetime.now()}".encode()).hexdigest()[:12]
        
        issue = {
            'id': issue_id,
            'group_id': group_id,
            'group_name': group['name'],
            'customer_id': hashlib.md5(customer_name.encode()).hexdigest()[:8],
            'customer_name': customer_name,
            'content': content,
            'issue_type': issue_type,
            'priority': priority,
            'created_at': datetime.now().isoformat()
        }
        
        self.db.add_issue(issue)
        print(f"✅ 新问题记录: [{issue_type}] {content[:50]}...")
        return issue
    
    def simulate_service_response(self, issue_id: str, handler: str):
        """模拟客服响应"""
        self.db.update_issue_response(issue_id, handler)
        print(f"✅ 问题 {issue_id} 已被 {handler} 响应")
    
    def check_and_send_alerts(self):
        """检查并发送预警"""
        alerts = self.alert_manager.check_alerts(self.db)
        
        for alert in alerts:
            issue = alert['issue']
            group = self._get_group_info(issue['group_id'])
            
            if alert['level'] == 'urgent':
                # 紧急预警：通知群管理员 + 飞书主管
                self.alert_manager.send_alert(alert, group['webhook'])
                # TODO: 发送飞书通知给主管
            else:
                # 普通预警：仅通知群管理员
                self.alert_manager.send_alert(alert, group['webhook'])
        
        return len(alerts)
    
    def generate_daily_report(self) -> str:
        """生成日报"""
        report = self.reporter.generate_report()
        
        # 保存到文件
        report_path = f"./logs/daily_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 日报已生成: {report_path}")
        return report
    
    def _get_group_info(self, group_id: str) -> Dict:
        """获取群信息"""
        for group in self.config['WECHAT_WORK']['MONITOR_GROUPS']:
            if group['group_id'] == group_id:
                return group
        return {'name': '未知群', 'webhook': '', 'admin': ''}


if __name__ == "__main__":
    # 测试运行
    service = WeComCustomerService()
    
    # 模拟客户提问
    print("=== 模拟客户提问 ===")
    issue1 = service.simulate_customer_message("GROUP_001", "客户张三", "请问这个系统怎么登录不了？报错502")
    issue2 = service.simulate_customer_message("GROUP_002", "客户李四", "我想申请开通管理员权限")
    issue3 = service.simulate_customer_message("GROUP_001", "客户王五", "紧急！系统崩溃了，无法访问！")
    
    # 模拟客服响应
    print("\n=== 模拟客服响应 ===")
    if issue1:
        service.simulate_service_response(issue1['id'], "客服小王")
    
    # 检查预警
    print("\n=== 检查预警 ===")
    alert_count = service.check_and_send_alerts()
    print(f"发现 {alert_count} 个需要预警的问题")
    
    # 生成日报
    print("\n=== 生成日报 ===")
    report = service.generate_daily_report()
    print(report)
