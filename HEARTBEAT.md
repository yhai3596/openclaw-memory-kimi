# HEARTBEAT.md - 系统心跳检查

## Self-Improving Check

- Read `./skills/self-improving/heartbeat-rules.md`
- Use `~/self-improving/heartbeat-state.md` for last-run markers and action notes
- If no file inside `~/self-improving/` changed since the last reviewed change, return `HEARTBEAT_OK`

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
5. **系统规则检查** - 验证 .rules/system-rules.json 状态
6. **持续迭代检查** - 技能更新、模式提取、用户画像更新

### 持续迭代检查清单

每次HEARTBEAT时自动执行：

- [ ] **技能更新检查**
  - 检查已安装skills是否有新版本
  - 检查ClawHub热门skills变化
  
- [ ] **子代理状态检查**
  - 验证多代理系统运行状态
  - 清理无用会话
  
- [ ] **模式提取**
  - 回顾近期完成的任务
  - 提取可复用的工作模式
  - 更新到AGENTS.md或相关skill
  
- [ ] **用户画像更新**
  - 检查memory文件中的新信息
  - 提取关键偏好和决策
  - 更新USER.md画像

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
