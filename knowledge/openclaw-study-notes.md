# OpenClaw 知识库学习笔记

> 创建时间: 2026-03-14
> 来源文档: 
> - /knowledge/openclaw-multi-agent.md (多智能体路由)
> - /knowledge/openclaw-github-readme.md (GitHub README)

---

## 核心概念理解

### 1. 什么是 OpenClaw?

OpenClaw 是一个**个人 AI 助手**运行框架，核心特点是：
- **本地优先**: 运行在自己的设备上
- **多通道**: 支持 WhatsApp、Telegram、Slack、Discord 等 20+ 通讯渠道
- **Gateway 架构**: WebSocket 控制平面，统一会话、通道、工具和事件管理

### 2. 多智能体路由 (Multi-Agent)

**关键理解**: 每个 `agentId` 是一个完全隔离的"大脑"

| 属性 | 说明 |
|------|------|
| 工作区 | 独立的文件系统、AGENTS.md/SOUL.md/USER.md |
| agentDir | 独立的认证配置、模型注册表 |
| 会话存储 | `~/.openclaw/agents/<agentId>/sessions` |
| 认证 | 每智能体独立的 `auth-profiles.json` |

**典型使用场景**:
- 多个 WhatsApp 号码 → 不同智能体
- 个人/工作分离 → 不同人格、不同工具权限
- 家庭群组专用智能体 → 严格的沙箱限制

### 3. 路由规则 (绑定优先级)

绑定是**确定性**的，**最具体的优先**:

1. `peer` 匹配 (精确私信/群组/频道 id)
2. `guildId` (Discord)
3. `teamId` (Slack)  
4. `accountId` 匹配
5. 渠道级匹配 (`accountId: "*"`)
6. 回退到默认智能体

### 4. 每智能体沙箱和工具配置 (v2026.1.6+)

可以为不同智能体配置不同的安全策略:

```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "sandbox": { "mode": "off" },
        // 无工具限制
      },
      {
        "id": "family",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit"]
        }
      }
    ]
  }
}
```

### 5. Agent-to-Agent 通信

- `sessions_list`: 发现活跃会话
- `sessions_history`: 获取会话历史
- `sessions_send`: 向其他会话发送消息
- `sessions_spawn`: 生成子代理会话

### 6. 安全模型

- **主会话 (main)**: 默认在主机上运行，完全访问
- **非主会话**: 可配置 Docker 沙箱隔离
- **配对机制**: 未知发送者需配对码才能通信

### 7. 支持的平台/节点

- **macOS**: 菜单栏、Voice Wake、Talk Mode、Canvas
- **iOS**: 节点模式、Canvas、相机、屏幕录制
- **Android**: 节点模式、Canvas、设备命令
- **Linux**: Gateway 主机（推荐远程部署）

### 8. 技能系统 (Skills)

- **Bundled**: 内置技能
- **Managed**: 通过 ClawHub 安装
- **Workspace**: 工作区本地技能 `~/.openclaw/workspace/skills/`

---

## 关键配置路径

```
~/.openclaw/openclaw.json          # 主配置
~/.openclaw/workspace/             # 默认工作区
~/.openclaw/agents/<agentId>/      # 智能体状态
~/.openclaw/agents/<agentId>/agent/auth-profiles.json  # 认证
~/.openclaw/credentials/           # 渠道凭证
```

---

## 实用 CLI 命令

```bash
openclaw onboard --install-daemon  # 初始化向导
openclaw agents list --bindings    # 查看绑定
openclaw doctor                    # 诊断问题
openclaw gateway --verbose         # 启动网关
openclaw agent --message "..."     # 与助手对话
```

---

## 后续可深入学习的方向

1. [ ] 完整的配置参考: https://docs.openclaw.ai/gateway/configuration
2. [ ] 架构设计: https://docs.openclaw.ai/concepts/architecture
3. [ ] 安全指南: https://docs.openclaw.ai/gateway/security
4. [ ] Docker + 沙箱: https://docs.openclaw.ai/install/docker
5. [ ] Skill 开发指南
6. [ ] Tailscale 远程访问配置
