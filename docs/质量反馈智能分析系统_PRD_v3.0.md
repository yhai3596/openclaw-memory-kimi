# 质量反馈智能分析系统 PRD

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v3.0 |
| 创建日期 | 2026-02-26 |
| 更新日期 | 2026-02-26 |
| 状态 | 定稿 |
| 作者 | Kimi Claw |

---

## 1. 项目背景

### 1.1 业务背景
- **产品**：空调硬件产品
- **市场**：美国市场
- **客户**：美国终端用户 + 安装商
- **售后系统**：Zoho Desk 租户系统
- **反馈形式**：Tickets 登记质量反馈
- **数据语言**：纯英文

### 1.2 现状痛点
| 痛点 | 影响 |
|------|------|
| 数据处理耗时 | 每周花大量时间洗数据，挤压问题分析时间 |
| 手工分类效率低 | 2000+ 条已分类，但人工跟不上新增速度 |
| 缺乏系统洞察 | 难以快速定位需要 QC 检讨的关键问题 |
| 响应滞后 | 批量问题发现晚，错过最佳处理窗口 |

### 1.3 核心目标
**不是做"数据分析系统"，而是构建"问题驱动的工作流"**

```
现在：每周 N 小时洗数据 → 没时间深挖 → 问题积压
目标：每周 30 分钟看简报 → 快速定位 → QC 检讨 → 质量改善
```

---

## 2. 产品定位

### 2.1 核心价值
| 维度 | 说明 |
|------|------|
| 用户 | 质量经理（主要使用者） |
| 场景 | 每周质量回顾、QC 小组启动、问题闭环跟踪 |
| 输出 | "本周质量简报"（飞书推送） |
| 价值 | 从"数据处理"转向"问题解决" |

### 2.2 成功标准
| 指标 | 目标 |
|------|------|
| 数据处理时间 | 每周 < 30 分钟 |
| 分类准确率 | ≥ 90% |
| QC 检讨触发 | 自动识别 ≥2 起的同类问题 |
| 简报生成 | 每周四早上 8:30 自动推送 |

---

## 3. 业务规则

### 3.1 质量等级计算（综合评分）

```
优先级得分 = 严重度 × 发生次数 × 趋势系数
```

**严重度配置（可修改，用户自定义）：**

| 问题现象 | 严重度 | 说明 |
|---------|--------|------|
| 安全风险（漏电、起火） | 5 | 最高优先级 |
| 功能失效（不制冷/不制热） | 4 | 核心功能 |
| 漏水 | 4 | 财产损失风险 |
| 安装问题 | 3 | 影响性能 |
| 噪音 | 3 | 影响体验 |
| 异味 | 3 | 健康担忧 |
| 显示故障 | 2 | 非核心功能 |
| 外观瑕疵 | 2 | 美观问题 |
| 其他 | 1 | 待分类 |

**趋势系数：**
- 环比增长 >100%：1.5
- 环比增长 50-100%：1.2
- 持平或下降：1.0

**等级划分：**
- 🔴 紧急：得分 ≥ 30 或 安全风险
- 🟡 关注：得分 15-29 或 新类型
- 🟢 跟踪：得分 < 15

### 3.2 同类问题定义
**维度：问题现象 + 机型**

示例：
- "Model-X + 不制冷" = 同类问题
- "Model-X + 噪音" = 不同类问题

### 3.3 QC 检讨触发条件
- 同一（问题现象 + 机型）本周 ≥ 2 起
- 或 🔴 紧急等级问题

### 3.4 数据来源
- **一期**：Zoho Desk 导出 Excel → 本地导入
- **二期**：Zoho API 自动对接（可选）

---

## 4. 功能需求

### 4.1 模块架构

```
┌─────────────────────────────────────────────────────────────┐
│                    质量反馈智能分析系统                        │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  数据导入层  │  数据处理层  │  分析展示层  │     预警通知层       │
├─────────────┼─────────────┼─────────────┼─────────────────────┤
│ Excel 导入  │ 数据清洗    │ 质量简报    │ 自动评分定级        │
│ 历史加载    │ 意图识别    │ 趋势图表    │ QC 触发提醒         │
│ 样本管理    │ 问题分类    │ 问题详情    │ 飞书推送            │
│             │ 置信度评估  │ 数据导出    │                     │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

### 4.2 功能清单

#### M1: 数据导入模块

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| Excel 导入 | 支持 Zoho 导出格式直接导入 | P0 |
| 字段映射 | 自动识别/手动配置字段对应关系 | P0 |
| 历史加载 | 批量导入历史数据（2000+ 样本） | P0 |
| 增量导入 | 支持仅导入新增数据 | P1 |
| 数据验证 | 检查必填字段、格式校验 | P0 |

**Excel 字段要求：**
- Ticket Id（工单编号）
- Subject（主题，主要问题描述）
- Ticket Description（详细描述）
- Ticket Type（工单类型，辅助判断）
- Condenser Model Number（外机型号）
- Created Time (Ticket)（创建时间）
- Category (Ticket)（现有分类，可选）

#### M2: 数据处理模块

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| 字段合并 | 综合 Subject + Description + Type | P0 |
| 数据清洗 | 过滤系统模板、去重、格式标准化 | P0 |
| 质量判断 | 区分质量问题 vs 非质量问题 | P0 |
| 意图识别 | 提取关键词、问题现象 | P0 |
| 问题分类 | 按预设标签自动分类 | P0 |
| 置信度评分 | 标注分类可信度（0-1） | P0 |
| 低置信度标记 | 置信度 < 0.75 标记需复核 | P0 |
| 人工复核 | 支持修改分类、补充标注 | P1 |
| 模型迭代 | 根据复核结果优化模型 | P2 |

**字段合并逻辑：**
```python
def merge_fields(row):
    parts = []
    
    # 1. Subject（主要描述）
    if pd.notna(row['Subject']) and row['Subject'] != '-':
        parts.append(str(row['Subject']))
    
    # 2. Description（过滤系统模板）
    if pd.notna(row['Ticket Description']):
        desc = str(row['Ticket Description'])
        # 过滤 Zoho Voice 自动生成内容
        if not desc.startswith('Hey\n\nYou have the following incoming call'):
            parts.append(desc)
    
    # 3. Type（辅助）
    if pd.notna(row['Ticket Type']) and row['Ticket Type'] != '-':
        parts.append(f"Type: {row['Ticket Type']}")
    
    return ' | '.join(parts)[:512]
```

**分类标签体系：**

| 一级分类 | 二级分类 | 英文关键词 |
|---------|---------|-----------|
| **非质量问题** | | |
| | 经销商咨询 | distributor, dealer, wholesale |
| | 销售咨询 | sales, become a dealer, interested in |
| | 保修注册 | warranty registration, register |
| | 税务咨询 | tax credit, federal |
| | 其他非质量 | other inquiry |
| **质量问题** | | |
| 功能失效 | 不制冷 | not cooling, warm air, no cool, blowing hot |
| 功能失效 | 不制热 | not heating, cold air, no heat, blowing cold |
| 功能失效 | 无法启动 | won't start, dead, not working |
| 漏水 | 室内机漏水 | leak, leaking, water drip, oil in drain pan |
| 漏水 | 室外机漏水 | outdoor leak, condenser leak |
| 噪音 | 外机噪音 | loud noise, vibration, rattling, outdoor unit noise |
| 噪音 | 内机噪音 | fan noise, whistling, indoor unit noise |
| 安装问题 | 安装不当 | installation, installed, mounting, piping issue |
| 安装问题 | 管道问题 | refrigerant line, tubing, connection |
| 显示故障 | 错误代码 | error code, P2, G3, fault, display error |
| 外观瑕疵 | 外观损坏 | scratch, dent, cosmetic damage |
| 其他 | 其他问题 | other issue |

#### M3: 分析展示模块

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| 质量简报 | 每周自动生成核心指标 | P0 |
| 问题列表 | 按优先级排序的问题清单 | P0 |
| 趋势图表 | 各类型问题时间趋势 | P0 |
| 机型分布 | 问题在机型上的分布 | P0 |
| 地区分布 | 问题在地区上的分布 | P1 |
| 问题详情 | 单问题的完整信息展示 | P0 |
| 数据导出 | Excel/CSV 导出 | P0 |

**简报内容示例：**

```
【本周质量简报】2026.02.24-03.02

━━━━━━━━━━━━━━━━━━━━
🔴 紧急（2项需 QC 检讨）
━━━━━━━━━━━━━━━━━━━━
1. 【Not Cooling | EODA18H-4860】得分: 48
   数量: 8起 | 上周: 3起 | 趋势: ↑167%
   严重度: 功能失效(4) × 8 × 1.5
   关键词: "not cooling", "warm air"
   [查看详情] [发起 QC]

━━━━━━━━━━━━━━━━━━━━
🟡 关注（1项）
━━━━━━━━━━━━━━━━━━━━
2. 【Noise | EODA18H-2436】得分: 18
   数量: 3起 | 上周: 0起 | 趋势: 新增
   关键词: "loud noise", "vibration"

━━━━━━━━━━━━━━━━━━━━
📊 本周概览
━━━━━━━━━━━━━━━━━━━━
总反馈: 42起 | 质量问题: 35起 | 非质量问题: 7起
需 QC 检讨: 2项 | 新增问题类型: 1项
TOP3: Not Cooling(8) | Noise(5) | Leaking(4)

━━━━━━━━━━━━━━━━━━━━
⚠️ 需人工复核（3项）
━━━━━━━━━━━━━━━━━━━━
- Ticket 9341: 置信度 0.65，描述模糊
- Ticket 9377: 新关键词组合
- Ticket 9416: 分类冲突
```

#### M4: 预警通知模块

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| 自动评分 | 根据规则自动计算优先级得分 | P0 |
| QC 触发提醒 | 自动识别需检讨的问题 | P0 |
| 简报推送 | 每周四 8:30 飞书推送 | P0 |
| 紧急预警 | 🔴 紧急问题即时推送 | P0 |
| 通知配置 | 支持配置接收人和渠道 | P1 |

---

## 5. 技术方案

### 5.1 技术栈

| 层级 | 选型 | 说明 |
|------|------|------|
| 数据导入 | pandas + openpyxl | Excel 处理 |
| 数据存储 | SQLite / PostgreSQL | 本地存储 |
| 分类模型 | **可配置** | 支持 BAAI/bge-m3, bert-base-uncased 等 |
| 训练框架 | transformers + sklearn | 模型微调 |
| 后端服务 | FastAPI | API 服务 |
| 前端界面 | Streamlit | 快速开发 |
| 简报生成 | Jinja2 + Markdown | 模板渲染 |
| 消息通知 | 飞书 Webhook | 推送简报 |
| 部署 | 本地 Python 环境 | 无需 Docker |

### 5.2 可配置模型列表

```yaml
# config.yaml - 模型配置
model:
  # 模型选择（可修改）
  name: "BAAI/bge-m3"  # 或其他选项
  
  # 支持的模型选项：
  # - "BAAI/bge-m3"              # 多语言，推荐
  # - "BAAI/bge-large-en-v1.5"   # 英文优化
  # - "bert-base-uncased"        # 经典英文
  # - "distilbert-base-uncased"  # 轻量快速
  # - "sentence-transformers/all-MiniLM-L6-v2"  # 极轻量
  
  device: "cuda"  # cuda 或 cpu
  max_length: 512
  batch_size: 32
  
  # 训练参数
  training:
    epochs: 5
    learning_rate: 2e-5
    warmup_steps: 100
```

### 5.3 部署方式

**方案：纯本地 Python 应用**

```
┌─────────────────────────────────────────┐
│           用户笔记本（i7+32G+4070）       │
│  ┌─────────────────────────────────┐    │
│  │     质量反馈分析系统（Python）     │    │
│  │  ┌─────────┐ ┌─────────┐       │    │
│  │  │ Streamlit│ │ 定时任务 │       │    │
│  │  │  界面   │ │ APScheduler│      │    │
│  │  └─────────┘ └─────────┘       │    │
│  │  ┌─────────┐ ┌─────────┐       │    │
│  │  │ SQLite  │ │ 模型文件 │       │    │
│  │  │  数据   │ │ bge-m3  │       │    │
│  │  └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 5.4 数据模型

```sql
-- 原始反馈表
CREATE TABLE feedback_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id VARCHAR(50),
    subject TEXT,
    description TEXT,
    ticket_type VARCHAR(50),
    model VARCHAR(100),
    model_serial VARCHAR(100),
    air_handler_model VARCHAR(100),
    air_handler_serial VARCHAR(100),
    region VARCHAR(100),
    created_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分类结果表
CREATE TABLE feedback_classified (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id INTEGER REFERENCES feedback_raw(id),
    is_quality_issue BOOLEAN,  -- 是否为质量问题
    primary_category VARCHAR(50),
    secondary_category VARCHAR(50),
    severity INTEGER, -- 1-5
    confidence FLOAT,
    keywords TEXT,
    merged_text TEXT,  -- 合并后的文本
    needs_review BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(50),
    reviewed_at TIMESTAMP,
    model_version VARCHAR(50),
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 周统计表
CREATE TABLE weekly_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start DATE,
    week_end DATE,
    total_count INTEGER,
    quality_count INTEGER,
    non_quality_count INTEGER,
    category_stats JSON,
    model_stats JSON,
    alert_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- QC 检讨记录表
CREATE TABLE qc_review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(50),
    model VARCHAR(100),
    feedback_ids TEXT, -- JSON array
    count INTEGER,
    severity_score INTEGER,
    status VARCHAR(20), -- pending / in_progress / resolved
    assigned_to VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
```

---

## 6. 配置文件

### 6.1 config.yaml

```yaml
system:
  name: "空调质量反馈分析系统"
  version: "1.0.0"
  
schedule:
  # 简报推送时间
  push_time: "周四 08:30"
  timezone: "America/New_York"  # 美国时间

model:
  # 模型选择（可修改）
  name: "BAAI/bge-m3"
  device: "cuda"  # cuda 或 cpu
  max_length: 512
  batch_size: 32
  
  # 训练参数
  training:
    epochs: 5
    learning_rate: 2e-5
    warmup_steps: 100
    test_size: 0.2

classification:
  # 质量判断阈值
  quality_threshold: 0.6
  
  # 置信度阈值
  confidence_threshold: 0.75
  
  # QC 触发阈值
  qc_threshold: 2
  
  # 同类问题定义
  group_by: ["primary_category", "model"]

severity:
  # 严重度配置（可修改）
  levels:
    安全风险: 5
    功能失效: 4
    漏水: 4
    安装问题: 3
    噪音: 3
    异味: 3
    显示故障: 2
    外观瑕疵: 2
    其他: 1
  
  # 问题现象到严重度的映射
  mapping:
    not_cooling: 4
    not_heating: 4
    wont_start: 4
    leaking: 4
    noise: 3
    installation: 3
    error_code: 2
    cosmetic: 2
    other: 1

trend:
  # 趋势系数
  coefficients:
    high: 1.5    # >100%
    medium: 1.2  # 50-100%
    low: 1.0     # <50%

alert:
  # 飞书 webhook
  feishu_webhook: ""
  
  # 紧急问题即时推送
  instant_alert: true
  
  # 接收人
  recipients: []

paths:
  data_dir: "./data"
  model_dir: "./models"
  export_dir: "./exports"
```

---

## 7. 实施计划

### 7.1 里程碑

```
M1: 基础框架（1周）
├── 项目结构搭建
├── 配置文件设计
├── Excel 导入功能
├── 字段合并逻辑
└── 基础界面

M2: 智能分类（2周）
├── 数据清洗流程
├── 质量判断逻辑
├── 分类模型训练（支持可配置模型）
├── 置信度评估
└── 人工复核界面

M3: 简报生成（1周）
├── 评分算法实现
├── 简报模板设计
├── 飞书推送对接
└── 定时任务（周四 8:30）

M4: 测试优化（1周）
├── 端到端测试
├── 模型选型对比（bge-m3 vs others）
├── 准确率调优
├── 用户体验优化
└── 文档编写
```

**总计：5 周 MVP 可用**

### 7.2 交付物

| 阶段 | 交付物 |
|------|--------|
| M1 | 可导入 Excel 的基础系统 |
| M2 | 可自动分类的测试版本 |
| M3 | 可生成简报的完整流程 |
| M4 | 生产可用版本 + 使用文档 |

---

## 8. 使用流程

### 8.1 每周操作流程

```
周四早上 8:30
    ↓
系统生成并推送简报（自动）
    ↓
你查看简报，确认 QC 检讨项
    ↓
发起 QC 小组（系统外）
    ↓
周三前
    ↓
从 Zoho 导出本周新数据
    ↓
导入系统
    ↓
人工复核低置信度项（如有）
    ↓
完成
```

### 8.2 首次使用流程

```
1. 配置 config.yaml（模型选择、严重度、推送时间等）
2. 准备 2000+ 样本 Excel（含分类标签）
3. 导入系统作为训练数据
4. 训练分类模型
5. 验证准确率
6. 配置飞书 Webhook
7. 导入本周新数据测试
8. 正式上线
```

---

## 9. 验收标准

### 9.1 功能验收

| 验收项 | 标准 |
|--------|------|
| Excel 导入 | 支持 Zoho 导出格式，无错误 |
| 字段合并 | 正确合并 Subject + Description + Type |
| 质量判断 | 正确区分质量问题 vs 非质量问题 |
| 分类准确率 | 测试集 ≥ 90% |
| 评分计算 | 符合业务规则（严重度 × 次数 × 趋势） |
| 简报生成 | 每周四 8:30 自动推送，内容完整 |
| QC 触发 | 正确识别 ≥2 起的同类问题 |
| 模型可配置 | 支持切换不同模型（bge-m3, bert等） |

### 9.2 性能验收

| 验收项 | 标准 |
|--------|------|
| 数据处理 | 100 条 < 10 秒 |
| 简报生成 | < 30 秒 |
| 界面响应 | < 3 秒 |

---

## 10. 待确认事项

- [x] 样本数据格式：Excel，57条，Subject 为主要描述
- [x] 机型字段：`Condenser Model Number`
- [x] 简报时间：周四 8:30
- [x] 语言：纯英文
- [x] 模型：可配置，支持 BAAI/bge-m3 等
- [x] 严重度：用户自定义配置文件
- [x] 分类字段：Subject + Description + Type
- [x] 非质量问题：单独分类

---

## 11. 附录

### 11.1 术语表

| 术语 | 解释 |
|------|------|
| QC 小组 | 质量控制小组，跨部门问题分析解决团队 |
| 置信度 | 模型对分类结果的确定程度（0-1） |
| 简报 | 每周质量状况总结报告 |
| 同类问题 | 相同问题现象 + 相同机型 |
| bge-m3 | BAAI 开源的多语言 Embedding 模型 |

### 11.2 文件清单

| 文件 | 说明 |
|------|------|
| main.py | 主程序入口 |
| app.py | Streamlit 界面 |
| config.yaml | 配置文件（模型、严重度、推送时间等） |
| models/ | 分类模型目录 |
| data/ | 数据库目录 |
| exports/ | 导出文件目录 |
| requirements.txt | 依赖清单 |

### 11.3 模型对比参考

| 模型 | 语言 | 大小 | 速度 | 准确率 | 适用场景 |
|------|------|------|------|--------|---------|
| BAAI/bge-m3 | 多语言 | 2.2GB | 中 | 高 | **推荐，平衡选择** |
| BAAI/bge-large-en-v1.5 | 英文 | 1.3GB | 中 | 高 | 纯英文优化 |
| bert-base-uncased | 英文 | 440MB | 快 | 中 | 快速验证 |
| distilbert-base-uncased | 英文 | 270MB | 很快 | 中 | 资源受限 |
| all-MiniLM-L6-v2 | 多语言 | 80MB | 极快 | 中 | 极致速度 |

---

**文档结束**
