# 企业微信客服群监控系统 - MVP版本

## 📁 项目结构

```
wecom-customer-service/
├── config/
│   └── config.yaml          # 配置文件
├── scripts/
│   ├── service_monitor.py   # 核心监控逻辑
│   ├── cron_job.py          # 定时任务
│   └── feishu_sync.py       # 飞书同步
├── data/
│   └── customer_service.db  # SQLite数据库
├── logs/
│   └── daily_report_*.md    # 日报文件
└── run.sh                   # 运行脚本
```

## 🚀 快速开始

### 1. 配置企业微信

编辑 `config/config.yaml`：

```yaml
WECHAT_WORK:
  CORP_ID: "你的企业ID"
  CORP_SECRET: "你的应用Secret"
  
  MONITOR_GROUPS:
    - group_id: "GROUP_001"
      name: "测试客户群A"
      webhook: "群机器人Webhook地址"
      admin: "@张三"
    - group_id: "GROUP_002"
      name: "测试客户群B"  
      webhook: "群机器人Webhook地址"
      admin: "@李四"
```

### 2. 运行测试

```bash
cd /root/.openclaw/workspace/projects/wecom-customer-service
./run.sh
```

### 3. 设置定时任务

```bash
# 添加定时任务（每5分钟检查一次）
crontab -e

# 添加以下行：
*/5 * * * * cd /root/.openclaw/workspace/projects/wecom-customer-service && python3 scripts/cron_job.py >> logs/cron.log 2>&1
```

## 📊 功能说明

### 已实现功能

- ✅ 问题识别与分类（技术问题/服务请求/投诉建议/紧急故障）
- ✅ 响应时间跟踪
- ✅ 超时预警（30分钟提醒/60分钟上报）
- ✅ 日报生成
- ✅ SQLite数据存储

### 待对接功能（需要企业微信配置）

- ⏳ 实时消息拉取（需开通会话内容存档）
- ⏳ 群机器人消息推送
- ⏳ 飞书文档同步

## 🔧 企业微信配置步骤

### 步骤1：创建自建应用

1. 登录企业微信管理后台
2. 应用管理 → 创建应用
3. 获取 `CorpID`、`AgentID`、`Secret`

### 步骤2：开通会话内容存档

1. 管理工具 → 会话内容存档
2. 按用户数购买服务
3. 配置公钥（用于解密消息）

### 步骤3：配置群机器人

1. 进入客户群 → 群设置
2. 添加群机器人
3. 复制 `Webhook地址`

### 步骤4：配置IP白名单

1. 应用管理 → 自建应用 → 企业可信IP
2. 添加服务器IP地址

## 📈 数据表结构

### issues（问题记录）
| 字段 | 说明 |
|------|------|
| id | 问题唯一ID |
| group_id | 群ID |
| customer_name | 客户名称 |
| content | 问题内容 |
| issue_type | 问题类型 |
| priority | 优先级 |
| created_at | 创建时间 |
| first_response_at | 首次响应时间 |
| status | 状态 |

## 📝 下一步计划

1. 对接企业微信API（获取真实消息）
2. 完善飞书文档同步
3. 添加Web管理界面
4. 支持更多群（从2个扩展到100+）
