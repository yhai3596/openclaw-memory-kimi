#!/usr/bin/env node
/**
 * ListenHub 播客生成工具
 * 自动生成 + 自动返回下载链接
 * 
 * 用法: node generate-podcast.js "主题内容" [speakerId1,speakerId2] [mode]
 */

const API_KEY = process.env.LISTENHUB_API_KEY || 'lh_sk_693430bd6ae633c0cc867331_d72d739c443d345d87dd67ad22d8051f7683b1e1b9a3e0c3';
const BASE_URL = 'https://api.marswave.ai/openapi/v1';

class ListenHubAPI {
  constructor(apiKey, baseUrl) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });
    const data = await response.json();
    
    if (data.code !== 0) {
      throw new Error(data.message);
    }
    return data.data;
  }

  async createPodcast(params) {
    return this.request('/podcast/episodes', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getStatus(episodeId) {
    return this.request(`/podcast/episodes/${episodeId}`);
  }

  async listSpeakers(language = 'zh') {
    const result = await this.request(`/speakers/list?language=${language}`);
    return result.items;
  }
}

async function generatePodcast(query, speakerIds, mode = 'quick') {
  const api = new ListenHubAPI(API_KEY, BASE_URL);
  
  console.log('🎙️ 开始生成播客...');
  console.log(`   主题: ${query}`);
  console.log(`   声音: ${speakerIds.join(', ')}`);
  console.log(`   模式: ${mode}`);
  console.log('');

  // 1. 创建任务
  const speakers = speakerIds.map(id => ({ speakerId: id }));
  const { episodeId } = await api.createPodcast({
    query,
    speakers,
    language: 'zh',
    mode,
  });

  console.log(`✅ 任务已创建: ${episodeId}`);
  console.log('⏳ 等待生成中... (约需 1-2 分钟)');
  console.log('');

  // 2. 首次等待 60 秒
  await sleep(60000);

  // 3. 轮询状态
  const maxWait = 300000; // 5分钟超时
  const interval = 10000; // 每10秒检查
  const startTime = Date.now();

  while (Date.now() - startTime < maxWait) {
    const episode = await api.getStatus(episodeId);
    
    if (episode.processStatus === 'success') {
      console.log('✅ 生成完成！\n');
      console.log('='.repeat(50));
      console.log('📋 任务信息：');
      console.log(`   任务ID: ${episodeId}`);
      console.log(`   标题: ${episode.title || 'N/A'}`);
      console.log(`   消耗积分: ${episode.credits || 0}`);
      console.log('');
      console.log('🔗 下载链接：');
      console.log(`   音频MP3: ${episode.audioUrl || 'N/A'}`);
      console.log(`   封面图: ${episode.cover || 'N/A'}`);
      console.log('='.repeat(50));
      return episode;
    }
    
    if (episode.processStatus === 'failed') {
      throw new Error(`生成失败: ${episode.failCode}`);
    }

    process.stdout.write('.');
    await sleep(interval);
  }

  throw new Error('生成超时');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getMyClonedVoices() {
  const api = new ListenHubAPI(API_KEY, BASE_URL);
  const speakers = await api.listSpeakers('zh');
  return speakers.filter(s => 
    s.speakerId.includes('voice-clone') || 
    s.demoAudioUrl.includes('voice-clone')
  );
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
🎙️ ListenHub 播客生成工具

用法:
  node generate-podcast.js "主题内容" [声音ID] [模式]

示例:
  # 使用默认声音生成
  node generate-podcast.js "人工智能的发展历史"

  # 使用指定声音生成
  node generate-podcast.js "企业AI培训" "chat-girl-105-cn"

  # 使用多个声音（双人对话）
  node generate-podcast.js "AI安全讨论" "chat-girl-105-cn,suzhe-45bbbe54"

  # 查看我的克隆声音
  node generate-podcast.js --my-voices

参数:
  主题内容     要生成的播客主题（必填）
  声音ID       说话人ID，多个用逗号分隔（默认: chat-girl-105-cn）
  模式         quick/standard/advanced（默认: quick）
    `);
    return;
  }

  // 查看我的克隆声音
  if (args[0] === '--my-voices') {
    console.log('🔍 查找你的克隆声音...\n');
    const voices = await getMyClonedVoices();
    if (voices.length === 0) {
      console.log('❌ 暂未发现克隆声音');
      console.log('💡 需要先访问 https://listenhub.ai 录制你的声音');
    } else {
      console.log('✅ 发现克隆声音：\n');
      voices.forEach(s => {
        console.log(`  - ${s.name} (${s.gender})`);
        console.log(`    ID: ${s.speakerId}`);
        console.log('');
      });
    }
    return;
  }

  const query = args[0];
  const speakerIds = args[1] ? args[1].split(',') : ['chat-girl-105-cn'];
  const mode = args[2] || 'quick';

  try {
    await generatePodcast(query, speakerIds, mode);
  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    process.exit(1);
  }
}

main();
