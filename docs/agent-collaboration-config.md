# OpenClaw 多 Agent 协作配置

> 配置文档版本: v1.0
> 适用 Agent: openclaw-bt (Master) + openclaw-n8n (Worker)
> 生成时间: 2026-03-04

---

## 1. 架构概述

```
┌─────────────────────────────────────────────────────┐
│                    飞书群 (消息总线)                   │
│  ┌──────────────────┐    ┌──────────────────┐       │
│  │   openclaw-bt    │<───>│  openclaw-n8n    │       │
│  │    (Master)      │    │    (Worker)      │       │
│  │                  │    │                  │       │
│  │  • 任务分发       │    │  • 执行任务       │       │
│  │  • 结果汇总       │    │  • 状态上报       │       │
│  │  • 状态监控       │    │  • 心跳汇报       │       │
│  └──────────────────┘    └──────────────────┘       │
└─────────────────────────────────────────────────────┘
```

---

## 2. Master Agent 配置 (openclaw-bt)

### 2.1 配置文件位置
```
~/.openclaw/config.json
```

### 2.2 Master 配置内容
```json
{
  "agent": {
    "id": "openclaw-bt",
    "role": "master",
    "workers": ["openclaw-n8n"],
    "heartbeatInterval": 300
  },
  "collaboration": {
    "enabled": true,
    "taskQueue": {
      "maxConcurrent": 3,
      "timeout": 600
    },
    "messageFormat": {
      "taskPrefix": "[任务]",
      "resultPrefix": "[结果]",
      "statusPrefix": "[状态]",
      "errorPrefix": "[错误]"
    }
  },
  "channels": {
    "feishu": {
      "appId": "YOUR_APP_ID",
      "appSecret": "YOUR_APP_SECRET",
      "encryptKey": "YOUR_ENCRYPT_KEY",
      "verificationToken": "YOUR_VERIFICATION_TOKEN"
    }
  }
}
```

### 2.3 Master 职责

| 功能 | 说明 |
|------|------|
| 任务分发 | 接收用户指令，分配给 Worker |
| 状态监控 | 定期检查 Worker 健康状态 |
| 结果汇总 | 收集 Worker 执行结果，统一汇报 |
| 故障转移 | Worker 离线时，记录并告警 |

### 2.4 Master 行为规则

```yaml
# 当收到用户任务时:
1. 解析任务类型
2. 查询 Worker 状态
3. 选择可用 Worker
4. 发送任务指令（带任务ID）
5. 设置超时计时器
6. 等待 Worker 回复
7. 汇总结果并汇报给用户

# 当收到 Worker 汇报时:
1. 验证任务ID匹配
2. 记录执行结果
3. 更新 Worker 状态
4. 如为最终结果，汇总后汇报

# 定时任务 (cron):
- 每5分钟: 检查 Worker 心跳
- 每30分钟: 生成协作状态报告
```

---

## 3. Worker Agent 配置 (openclaw-n8n)

### 3.1 配置文件位置
```
~/.openclaw/config.json
```

### 3.2 Worker 配置内容
```json
{
  "agent": {
    "id": "openclaw-n8n",
    "role": "worker",
    "master": "openclaw-bt",
    "capabilities": [
      "server_check",
      "file_operation",
      "web_search",
      "code_execution"
    ],
    "heartbeatInterval": 60
  },
  "collaboration": {
    "enabled": true,
    "autoAccept": false,
    "maxTaskDuration": 300
  },
  "channels": {
    "feishu": {
      "appId": "YOUR_APP_ID",
      "appSecret": "YOUR_APP_SECRET",
      "encryptKey": "YOUR_ENCRYPT_KEY",
      "verificationToken": "YOUR_VERIFICATION_TOKEN"
    }
  }
}
```

### 3.3 Worker 职责

| 功能 | 说明 |
|------|------|
| 任务执行 | 接收并执行 Master 分派的任务 |
| 状态上报 | 定期向 Master 汇报健康状态 |
| 结果反馈 | 任务完成后，主动汇报结果 |
| 能力注册 | 向 Master 声明可执行的任务类型 |

### 3.4 Worker 行为规则

```yaml
# 当收到 Master 任务时:
1. 验证 Master 身份
2. 检查任务是否在能力范围内
3. 回复 "接受" 或 "拒绝"
4. 如接受，开始执行任务
5. 执行中可发送进度更新
6. 完成后发送最终结果

# 定时任务 (cron):
- 每1分钟: 向 Master 发送心跳
- 每5分钟: 汇报当前负载状态

# 能力声明:
- server_check: 服务器健康检查
- file_operation: 文件读写操作
- web_search: 网络搜索
- code_execution: 代码执行
```

---

## 4. 通信协议

### 4.1 消息格式标准

```
[@目标Agent] [消息类型] 内容

消息类型:
- [任务]     - Master 分配给 Worker 的任务
- [接受]     - Worker 接受任务
- [拒绝]     - Worker 拒绝任务（附带原因）
- [进度]     - 任务执行中的进度更新
- [结果]     - 任务最终结果
- [状态]     - 状态汇报/心跳
- [错误]     - 错误报告
```

### 4.2 消息示例

**Master → Worker (任务分配)**
```
@openclaw-n8n [任务] 执行服务器状态检查
任务ID: #TASK-001
类型: server_check
超时: 300秒
```

**Worker → Master (接受任务)**
```
@openclaw-bt [接受] 任务 #TASK-001
预计完成时间: 60秒
```

**Worker → Master (进度更新)**
```
@openclaw-bt [进度] 任务 #TASK-001
进度: 50%
状态: 正在收集系统信息...
```

**Worker → Master (结果汇报)**
```
@openclaw-bt [结果] 任务 #TASK-001 完成
CPU: 15%
内存: 45%
磁盘: 60%
运行时间: 15天
```

**Worker → Master (心跳)**
```
@openclaw-bt [状态] 心跳
Agent: openclaw-n8n
状态: 在线
负载: 低
待处理任务: 0
```

---

## 5. 任务类型定义

### 5.1 标准任务类型

| 类型 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| server_check | 服务器健康检查 | target: 服务器标识 | CPU/内存/磁盘/网络状态 |
| file_operation | 文件操作 | action: read/write/delete<br>path: 文件路径<br>content: 内容 | 操作结果 |
| web_search | 网络搜索 | query: 搜索关键词<br>limit: 结果数量 | 搜索结果列表 |
| code_execution | 代码执行 | language: 语言<br>code: 代码<br>timeout: 超时 | 执行输出 |
| data_sync | 数据同步 | source: 源路径<br>target: 目标路径 | 同步状态 |

### 5.2 自定义任务类型

可在 `~/.openclaw/skills/collaboration/tasks/` 下添加自定义任务定义：

```json
{
  "name": "custom_task",
  "description": "自定义任务描述",
  "params": {
    "param1": { "type": "string", "required": true },
    "param2": { "type": "number", "default": 10 }
  },
  "timeout": 120,
  "handler": "./handlers/custom_task.js"
}
```

---

## 6. 故障处理

### 6.1 Worker 离线

```yaml
检测: Master 5分钟内未收到 Worker 心跳
处理:
  1. 标记 Worker 为离线
  2. 告警通知用户
  3. 将待处理任务重新分配
  4. 记录故障日志
```

### 6.2 任务超时

```yaml
检测: 任务执行超过设定超时时间
处理:
  1. 向 Worker 发送取消指令
  2. 标记任务为失败
  3. 记录超时原因
  4. 根据策略决定是否重试
```

### 6.3 任务失败

```yaml
检测: Worker 返回 [错误] 消息
处理:
  1. 记录错误信息
  2. 分析失败原因
  3. 如为可重试错误，重新分配
  4. 如为不可重试错误，通知用户
```

---
## 7. 部署步骤

### 7.1 Master 部署 (openclaw-bt)

```bash
# 1. 登录 openclaw-bt 服务器
ssh openclaw-bt

# 2. 备份原配置
cp ~/.openclaw/config.json ~/.openclaw/config.json.bak

# 3. 应用新配置
cp /path/to/master-config.json ~/.openclaw/config.json

# 4. 重启服务
openclaw gateway restart

# 5. 验证状态
openclaw status
```

### 7.2 Worker 部署 (openclaw-n8n)

```bash
# 1. 登录 openclaw-n8n 服务器
ssh openclaw-n8n

# 2. 备份原配置
cp ~/.openclaw/config.json ~/.openclaw/config.json.bak

# 3. 应用新配置
cp /path/to/worker-config.json ~/.openclaw/config.json

# 4. 重启服务
openclaw gateway restart

# 5. 验证状态
openclaw status
```

### 7.3 协作验证

```bash
# 在群里发送测试指令
@openclaw-bt [任务分发] 执行协作测试

# 预期响应:
# 1. openclaw-bt 回复 "已接收，正在分配..."
# 2. openclaw-n8n 回复 "[接受] 任务..."
# 3. openclaw-n8n 回复 "[结果] 任务完成..."
# 4. openclaw-bt 回复 "汇总结果..."
```

---

## 8. 监控与日志

### 8.1 日志位置

| Agent | 日志路径 |
|-------|----------|
| openclaw-bt | `~/.openclaw/logs/master.log` |
| openclaw-n8n | `~/.openclaw/logs/worker.log` |

### 8.2 关键指标

```yaml
Master 指标:
  - 任务分发成功率
  - Worker 在线率
  - 任务平均处理时间
  - 故障转移次数

Worker 指标:
  - 任务接受率
  - 任务成功率
  - 平均执行时间
  - 资源使用率
```

---

## 9. 扩展计划

### 9.1 添加新 Worker

当 openclaw-tx1、openclaw-mm、openclaw-AL 修复后：

1. 为每个 Agent 分配角色和 capabilities
2. 更新 Master 配置中的 workers 列表
3. 部署 Worker 配置并启动
4. 验证注册和心跳

### 9.2 多 Master 架构（未来）

```
┌─────────────────────────────────────────┐
│              负载均衡层                  │
│         (根据任务类型路由)                │
├─────────────────────────────────────────┤
│  Master-A      Master-B      Master-C   │
│  (Web任务)    (数据任务)    (系统任务)   │
└─────────────────────────────────────────┘
```

---

## 10. 附录

### 10.1 快速命令参考

```bash
# 查看 Agent 状态
openclaw status

# 查看协作日志
tail -f ~/.openclaw/logs/collaboration.log

# 手动触发心跳检查
openclaw collaboration heartbeat

# 查看任务队列
openclaw collaboration queue

# 强制同步配置
openclaw collaboration sync
```

### 10.2 配置文件模板

见本文档第 2、3 节。

---

*配置文档版本: v1.0*
*生成者: kimiclaw*
*适用场景: 双 Agent 主从协作*
