# PRD: AI 对话管理后台 (ChatAdmin)

> 生成时间: 2026-03-04
> 生成者: OpenClaw
> 目标实现者: Cursor/Trae

---

## 1. 项目概述

### 1.1 产品定位
一个用于管理多平台 AI 对话的后台系统，支持查看、搜索、归档、分析对话记录。

### 1.2 核心功能
- 多平台对话聚合（飞书、Telegram、Discord）
- 对话记录搜索与筛选
- 对话标签与归档
- 对话统计分析
- 用户管理

---

## 2. 技术栈

- **前端**: React 18 + TypeScript + Tailwind CSS
- **后端**: Node.js + Express + TypeScript
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **状态管理**: Zustand
- **UI 组件**: shadcn/ui

---

## 3. 数据库设计

### 3.1 对话表 (conversations)
```sql
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  platform TEXT NOT NULL, -- feishu, telegram, discord
  channel_id TEXT NOT NULL,
  channel_name TEXT,
  user_id TEXT NOT NULL,
  user_name TEXT,
  content TEXT NOT NULL,
  message_type TEXT DEFAULT 'text', -- text, image, file
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_archived BOOLEAN DEFAULT 0,
  tags TEXT -- JSON array
);
```

### 3.2 用户表 (users)
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  platform TEXT NOT NULL,
  platform_user_id TEXT NOT NULL,
  name TEXT,
  avatar_url TEXT,
  first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  message_count INTEGER DEFAULT 0,
  UNIQUE(platform, platform_user_id)
);
```

### 3.3 标签表 (tags)
```sql
CREATE TABLE tags (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  color TEXT DEFAULT '#3b82f6',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. API 设计

### 4.1 对话相关
```
GET    /api/conversations          # 获取对话列表（支持分页、筛选）
GET    /api/conversations/:id      # 获取单条对话
POST   /api/conversations          # 创建对话
PUT    /api/conversations/:id      # 更新对话
DELETE /api/conversations/:id      # 删除对话
POST   /api/conversations/:id/tags # 添加标签
```

### 4.2 筛选参数
```
GET /api/conversations?platform=feishu&startDate=2026-03-01&endDate=2026-03-04&keyword=hello&isArchived=false
```

### 4.3 统计相关
```
GET /api/stats/overview    # 总览数据
GET /api/stats/platform    # 各平台分布
GET /api/stats/timeline    # 时间线数据
```

---

## 5. 页面设计

### 5.1 布局结构
```
┌─────────────────────────────────────────┐
│  Sidebar    │        Main Content       │
│             │                           │
│  - Dashboard│  - Header (搜索/筛选)      │
│  - 对话列表  │  - 数据表格/卡片           │
│  - 用户管理  │  - 分页                   │
│  - 统计分析  │                           │
│  - 设置     │                           │
└─────────────────────────────────────────┘
```

### 5.2 页面清单

| 页面 | 路径 | 功能 |
|------|------|------|
| 仪表盘 | / | 总览统计、最近对话 |
| 对话列表 | /conversations | 对话管理、搜索、筛选 |
| 对话详情 | /conversations/:id | 单条对话详情 |
| 用户列表 | /users | 用户管理 |
| 统计分析 | /analytics | 图表统计 |
| 设置 | /settings | 系统配置 |

---

## 6. 组件清单

### 6.1 通用组件
- `DataTable` - 数据表格（支持排序、筛选、分页）
- `SearchInput` - 搜索输入框
- `DateRangePicker` - 日期范围选择
- `PlatformBadge` - 平台标识徽章
- `TagSelector` - 标签选择器

### 6.2 页面组件
- `ConversationCard` - 对话卡片
- `ConversationList` - 对话列表
- `StatsCard` - 统计卡片
- `LineChart` - 折线图
- `PieChart` - 饼图

---

## 7. 数据结构示例

### 7.1 对话记录
```json
{
  "id": "conv_001",
  "platform": "feishu",
  "channel_id": "oc_xxx",
  "channel_name": "技术交流群",
  "user_id": "ou_xxx",
  "user_name": "张三",
  "content": "这个 API 怎么调用？",
  "message_type": "text",
  "created_at": "2026-03-04T15:30:00Z",
  "is_archived": false,
  "tags": ["问题", "API"]
}
```

### 7.2 统计概览
```json
{
  "totalConversations": 12580,
  "totalUsers": 342,
  "todayConversations": 156,
  "platformDistribution": {
    "feishu": 5234,
    "telegram": 4521,
    "discord": 2825
  }
}
```

---

## 8. 实现优先级

### P0 - 核心功能
- [ ] 项目初始化（前后端）
- [ ] 数据库设计与连接
- [ ] 对话列表页面
- [ ] 基础 CRUD API

### P1 - 重要功能
- [ ] 搜索与筛选
- [ ] 用户管理
- [ ] 仪表盘统计

### P2 - 增强功能
- [ ] 标签系统
- [ ] 数据分析图表
- [ ] 导出功能

---

## 9. 验收标准

- [ ] 能正常启动前后端服务
- [ ] 能创建、查看、编辑、删除对话
- [ ] 能按平台、日期、关键词筛选
- [ ] 仪表盘显示正确的统计数据
- [ ] 界面美观、响应式适配

---

*本 PRD 由 OpenClaw 生成，供 Cursor/Trae 实现参考。*
