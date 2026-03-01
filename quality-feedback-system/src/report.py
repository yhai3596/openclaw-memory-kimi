"""
简报生成模块
"""
import yaml
import json
from datetime import datetime, timedelta
from collections import defaultdict
from jinja2 import Template

class ReportGenerator:
    def __init__(self, config_path="./config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def calculate_score(self, severity, count, trend_ratio):
        """计算优先级得分"""
        # 趋势系数
        if trend_ratio > 1.0:
            coeff = self.config['trend']['coefficients']['high']
        elif trend_ratio > 0.5:
            coeff = self.config['trend']['coefficients']['medium']
        else:
            coeff = self.config['trend']['coefficients']['low']
        
        return severity * count * coeff
    
    def get_level(self, score, is_safety=False):
        """根据得分判断等级"""
        if is_safety or score >= 30:
            return '🔴 紧急'
        elif score >= 15:
            return '🟡 关注'
        else:
            return '🟢 跟踪'
    
    def analyze_weekly_data(self, feedbacks, prev_feedbacks=None):
        """分析一周数据"""
        # 按类别和机型分组
        groups = defaultdict(list)
        
        for fb in feedbacks:
            if not fb.get('is_quality_issue'):
                continue
            
            key = (fb.get('primary_category'), fb.get('model'))
            groups[key].append(fb)
        
        # 计算上周数据（用于趋势）
        prev_groups = defaultdict(int)
        if prev_feedbacks:
            for fb in prev_feedbacks:
                if fb.get('is_quality_issue'):
                    key = (fb.get('primary_category'), fb.get('model'))
                    prev_groups[key] += 1
        
        # 生成分析结果
        results = []
        for (category, model), items in groups.items():
            count = len(items)
            prev_count = prev_groups.get((category, model), 0)
            
            # 计算趋势
            if prev_count > 0:
                trend_ratio = (count - prev_count) / prev_count
            else:
                trend_ratio = 999 if count > 0 else 0  # 新增
            
            # 计算得分
            severity = items[0].get('severity', 1)
            score = self.calculate_score(severity, count, trend_ratio)
            
            # 收集关键词
            all_keywords = []
            for item in items:
                keywords = item.get('keywords', '[]')
                if isinstance(keywords, str):
                    try:
                        keywords = json.loads(keywords)
                    except:
                        keywords = []
                all_keywords.extend(keywords)
            
            top_keywords = list(set(all_keywords))[:5]
            
            results.append({
                'category': category,
                'model': model or 'Unknown',
                'count': count,
                'prev_count': prev_count,
                'trend_ratio': trend_ratio,
                'severity': severity,
                'score': score,
                'level': self.get_level(score),
                'keywords': top_keywords,
                'feedback_ids': [item['id'] for item in items],
                'needs_qc': count >= self.config['classification']['qc_threshold']
            })
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def generate_report(self, week_start, week_end, feedbacks, prev_feedbacks=None):
        """生成周报"""
        # 分析数据
        analysis = self.analyze_weekly_data(feedbacks, prev_feedbacks)
        
        # 统计
        total = len(feedbacks)
        quality_count = sum(1 for f in feedbacks if f.get('is_quality_issue'))
        non_quality_count = total - quality_count
        
        # 分组
        emergency = [a for a in analysis if '紧急' in a['level']]
        attention = [a for a in analysis if '关注' in a['level']]
        tracking = [a for a in analysis if '跟踪' in a['level']]
        
        # QC 触发项
        qc_items = [a for a in analysis if a['needs_qc']]
        
        # 需复核项
        review_items = [f for f in feedbacks if f.get('needs_review')]
        
        # 生成报告文本
        report = self.format_report(
            week_start, week_end,
            total, quality_count, non_quality_count,
            emergency, attention, tracking,
            qc_items, review_items
        )
        
        return {
            'text': report,
            'stats': {
                'total': total,
                'quality': quality_count,
                'non_quality': non_quality_count,
                'emergency': len(emergency),
                'attention': len(attention),
                'qc_needed': len(qc_items),
                'needs_review': len(review_items)
            },
            'details': analysis
        }
    
    def format_report(self, week_start, week_end, total, quality, non_quality,
                      emergency, attention, tracking, qc_items, review_items):
        """格式化报告文本"""
        
        template = Template("""
【本周质量简报】{{ week_start }} ~ {{ week_end }}

━━━━━━━━━━━━━━━━━━━━
🔴 紧急（{{ emergency|length }}项需 QC 检讨）
━━━━━━━━━━━━━━━━━━━━
{% for item in emergency %}
{{ loop.index }}. 【{{ item.category }} | {{ item.model }}】得分: {{ "%.0f"|format(item.score) }}
   数量: {{ item.count }}起 | 上周: {{ item.prev_count }}起 | 
   {% if item.trend_ratio > 10 %}趋势: 新增{% elif item.trend_ratio > 0 %}趋势: ↑{{ "%.0f"|format(item.trend_ratio * 100) }}%{% else %}趋势: 持平{% endif %}
   严重度: {{ item.severity }} × {{ item.count }} × {{ "%.1f"|format(item.score / (item.severity * item.count) if item.severity * item.count > 0 else 1) }}
   {% if item.keywords %}关键词: {{ ", ".join(item.keywords) }}{% endif %}
{% endfor %}

{% if attention %}
━━━━━━━━━━━━━━━━━━━━
🟡 关注（{{ attention|length }}项）
━━━━━━━━━━━━━━━━━━━━
{% for item in attention %}
{{ loop.index }}. 【{{ item.category }} | {{ item.model }}】得分: {{ "%.0f"|format(item.score) }}
   数量: {{ item.count }}起 | 上周: {{ item.prev_count }}起
{% endfor %}
{% endif %}

━━━━━━━━━━━━━━━━━━━━
📊 本周概览
━━━━━━━━━━━━━━━━━━━━
总反馈: {{ total }}起 | 质量问题: {{ quality }}起 | 非质量问题: {{ non_quality }}起
需 QC 检讨: {{ qc_items|length }}项 | 新增问题类型: {{ emergency|length + attention|length }}项

{% if review_items %}
━━━━━━━━━━━━━━━━━━━━
⚠️ 需人工复核（{{ review_items|length }}项）
━━━━━━━━━━━━━━━━━━━━
{% for item in review_items %}
- Ticket {{ item.ticket_id }}: 置信度 {{ "%.2f"|format(item.confidence) }}
{% endfor %}
{% endif %}
""")
        
        return template.render(
            week_start=week_start.strftime('%Y.%m.%d'),
            week_end=week_end.strftime('%Y.%m.%d'),
            total=total,
            quality=quality,
            non_quality=non_quality,
            emergency=emergency,
            attention=attention,
            tracking=tracking,
            qc_items=qc_items,
            review_items=review_items
        )
    
    def save_weekly_stats(self, db, week_start, week_end, stats, details):
        """保存周统计到数据库"""
        conn = db.conn if hasattr(db, 'conn') else None
        if not conn:
            from .database import Database
            db = Database()
        
        # 统计类别分布
        category_stats = defaultdict(int)
        model_stats = defaultdict(int)
        
        for d in details:
            category_stats[d['category']] += d['count']
            model_stats[d['model']] += d['count']
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weekly_stats
            (week_start, week_end, total_count, quality_count, non_quality_count,
             category_stats, model_stats, alert_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            week_start.date(),
            week_end.date(),
            stats['total'],
            stats['quality'],
            stats['non_quality'],
            json.dumps(dict(category_stats)),
            json.dumps(dict(model_stats)),
            stats['qc_needed']
        ))
        
        conn.commit()
        conn.close()
