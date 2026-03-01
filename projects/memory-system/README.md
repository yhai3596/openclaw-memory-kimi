# 记忆系统 (Memory System)

## 目标
确保所有对话、记忆、配置持久保存，可随环境迁移

## 组件
- ✅ 本地 Git 仓库
- ✅ 自动备份脚本 (.backup.sh)
- ✅ 心跳检查 (.heartbeat.sh)
- ✅ 定时任务 (每小时)
- ⏳ 远程仓库 (等待 GitHub)

## 文件结构
```
/root/.openclaw/workspace/
├── IDENTITY.md      # AI 身份
├── USER.md          # 用户信息
├── SOUL.md          # 性格设定
├── MEMORY.md        # 长期记忆
├── TODO.md          # 待办清单
├── memory/          # 每日日志
└── .git/            # Git 仓库
```

## 状态
- [x] 本地备份: 运行中
- [x] 心跳通知: 运行中
- [ ] 云端同步: 等待 GitHub 仓库

## 下一步
等待用户提供 GitHub 仓库地址: `https://github.com/yhai3596/openclaw-memory`
