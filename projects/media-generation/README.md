# 多媒体生成能力部署计划

## 目标
自建播客、图片、音频、视频生成能力，不依赖第三方闭源服务

## 组件

### 1. Podcast-Generator（播客生成）
- 开源地址: https://github.com/justlovemaki/Podcast-Generator
- 功能: AI 生成播客脚本 + TTS 合成
- 部署方式: Docker 或 Python 直接运行
- 需要: 一台云服务器（建议 2核4G+）

### 2. 图片生成
- 方案A: Stable Diffusion (需要 GPU)
- 方案B: 调用 API (DALL-E, Midjourney, Pollinations)

### 3. 视频合成
- 工具: FFmpeg
- 流程: 音频 + 图片序列 → 视频

## 待办
- [ ] 选择部署服务器
- [ ] 部署 Podcast-Generator
- [ ] 配置 TTS 服务
- [ ] 测试端到端生成
- [ ] 集成到 OpenClaw 工作流

## 使用场景
1. 公众号文章 → 自动转音频播客
2. 主题/关键词 → 生成解说视频
3. 金句/观点 → 生成配图
