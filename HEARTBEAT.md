# HEARTBEAT.md - 系统心跳检查

## 自动执行项（无需询问用户）

### 1. 记忆自动备份检查
每次心跳时执行:
```bash
cd /root/.openclaw/workspace && ./.backup.sh
```

### 2. 远程仓库状态检查
- 检查是否配置了远程仓库
- 如果没有，提醒用户配置

## 执行记录

备份日志: `/root/.openclaw/workspace/.backup.log`

---

如果以上任务都已正常执行，回复: HEARTBEAT_OK
