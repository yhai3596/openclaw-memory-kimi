# ListenHub Skill

OpenClaw 集成的多媒体生成能力

## 功能

- 🎙️ **播客生成** - AI 生成 1-2 人对话播客
- 🎬 **解说视频** - 文章/主题转视频 + AI 配图
- 🔊 **语音朗读** - 文本转自然语音
- 🖼️ **图片生成** - 根据描述生成图片

## 安装

```bash
cd /root/.openclaw/workspace/skills/listenhub
chmod +x setup.sh
./setup.sh
```

## 配置

```bash
# 配置 API Key
python3 listenhub_skill.py --config
# 输入你的 ListenHub API Key
```

## 使用

### 生成播客
```bash
python3 listenhub_skill.py podcast "AI 如何改变企业培训"
```

### 生成解说视频
```bash
python3 listenhub_skill.py video "https://你的文章链接.com"
```

### 语音朗读
```bash
python3 listenhub_skill.py audio "这是一段要朗读的文本"
```

### 生成图片
```bash
python3 listenhub_skill.py image "山顶的日落，金色光芒"
```

## API 文档

https://listenhub.ai/docs/zh/skills

## 状态

- [x] 基础框架搭建
- [ ] 接入真实 API（等待 API Key）
- [ ] 测试端到端流程
- [ ] 集成到 OpenClaw 主流程
