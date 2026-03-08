#!/usr/bin/env node
/**
 * ListenHub 内容生成工具
 * 支持：播客、语音合成
 * 自动生成 + 自动返回下载链接
 * 
 * 用法: ./listenhub [类型] "主题内容" [选项]
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

  async getPodcastStatus(episodeId) {
    return this.request(`/podcast/episodes/${episodeId}`);
  }

  async createSpeech(params) {
    return this.request('/speech', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async listSpeakers(language = 'zh') {
    const result = await this.request(`/speakers/list?language=${language}`);
    return result.items;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function pollTask(api, id, maxWait = 300000) {
  const interval = 10000;
  const startTime = Date.now();

  await sleep(60000);

  while (Date.now() - startTime < maxWait) {
    try {
      const status = await api.getPodcastStatus(id);
      
      if (status.processStatus === 'success') {
        return status;
      }
      
      if (status.processStatus === 'failed') {
        throw new Error(`生成失败: ${status.failCode}`);
      }
    } catch (e) {
      process.stdout.write('?');
    }

    process.stdout.write('.');
    await sleep(interval);
  }

  throw new Error('生成超时');
}

async function generatePodcast(api, query, speakerIds, mode = 'quick') {
  console.log('🎙️ 开始生成播客...');
  console.log(`   主题: ${query}`);
  console.log(`   声音: ${speakerIds.join(', ')}`);
  console.log(`   模式: ${mode}`);
  console.log('');

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

  const result = await pollTask(api, episodeId);

  console.log('\n✅ 播客生成完成！\n');
  console.log('='.repeat(50));
  console.log('📋 任务信息：');
  console.log(`   任务ID: ${episodeId}`);
  console.log(`   标题: ${result.title || 'N/A'}`);
  console.log(`   消耗积分: ${result.credits || 0}`);
  console.log('');
  console.log('🔗 下载链接：');
  console.log(`   音频MP3: ${result.audioUrl || 'N/A'}`);
  console.log(`   封面图: ${result.cover || 'N/A'}`);
  console.log('='.repeat(50));

  return result;
}

async function generateSpeech(api, text, speakerId) {
  console.log('🗣️ 开始生成语音...');
  console.log(`   文字: ${text.slice(0, 50)}...`);
  console.log(`   声音: ${speakerId}`);
  console.log('');

  const result = await api.createSpeech({
    text,
    speakerId,
    language: 'zh',
  });

  console.log('✅ 语音生成完成！\n');
  console.log('='.repeat(50));
  console.log('🔗 下载链接：');
  console.log(`   音频: ${result.audioUrl || result.url || 'N/A'}`);
  console.log('='.repeat(50));

  return result;
}

async function getMyClonedVoices(api) {
  const speakers = await api.listSpeakers('zh');
  return speakers.filter(s => 
    s.speakerId.includes('voice-clone') || 
    s.demoAudioUrl.includes('voice-clone')
  );
}

async function showHelp() {
  console.log(`
🎙️ ListenHub 内容生成工具

📌 支持的类型:
  podcast  - 生成AI播客（音频）
  speech   - 文字转语音

📖 用法:
  # 生成播客
  ./listenhub podcast "主题内容" [声音ID] [模式]

  # 文字转语音
  ./listenhub speech "要朗读的文字" [声音ID]

📋 示例:
  # 播客（默认声音）
  ./listenhub podcast "人工智能的发展"

  # 播客（你的克隆声音）
  ./listenhub podcast "企业AI培训" "voice-clone-xxx"

  # 文字转语音
  ./listenhub speech "欢迎使用AI服务" "chat-girl-105-cn"

📌 其他命令:
  ./listenhub --my-voices    查看你的克隆声音
  ./listenhub --help         显示此帮助

💡 提示:
  视频和幻灯片功能仅在 ListenHub 网站提供
  访问: https://listenhub.ai
`);
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    await showHelp();
    return;
  }

  const api = new ListenHubAPI(API_KEY, BASE_URL);

  if (args[0] === '--my-voices') {
    console.log('🔍 查找你的克隆声音...\n');
    const voices = await getMyClonedVoices(api);
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

  const type = args[0];
  const query = args[1];

  if (!query) {
    console.log('❌ 错误: 缺少主题内容');
    console.log('用法: ./listenhub [类型] "主题内容" [选项]');
    return;
  }

  try {
    switch (type) {
      case 'podcast':
        const speakerIds = args[2] ? args[2].split(',') : ['chat-girl-105-cn'];
        const mode = args[3] || 'quick';
        await generatePodcast(api, query, speakerIds, mode);
        break;
      
      case 'speech':
        const speechSpeakerId = args[2] || 'chat-girl-105-cn';
        await generateSpeech(api, query, speechSpeakerId);
        break;
      
      default:
        console.log(`❌ 未知类型: ${type}`);
        console.log('支持的类型: podcast, speech');
        console.log('注意: 视频和幻灯片请在 https://listenhub.ai 网站生成');
        process.exit(1);
    }
  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    process.exit(1);
  }
}

main();
