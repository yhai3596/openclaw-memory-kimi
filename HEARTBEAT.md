# HEARTBEAT.md - 系统心跳检查

## 自动执行项（无需询问用户）

执行完整的心跳检查:
```bash
cd /root/.openclaw/workspace && ./.heartbeat.sh && cat .heartbeat_notify
```

这会完成以下任务：
1. **自动备份** - 提交所有变更到 Git
2. **关键文件检查** - 确保 IDENTITY.md, USER.md, SOUL.md 存在
3. **每日记忆创建** - 自动创建当日记忆日志
4. **远程仓库检查** - 提醒配置云端备份

## 通知机制

心跳执行完成后，会生成 `.heartbeat_notify` 文件，包含：
- 备份状态
- 远程仓库状态
- 新创建的文件

**必须将通知内容发送给用户**，不要静默执行。

## 日志文件

- 备份日志: `.backup.log`
- 心跳日志: `.heartbeat.log`
- 每日记忆: `memory/YYYY-MM-DD.md`

---

发送通知后，回复: HEARTBEAT_OK
