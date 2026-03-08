/**
 * ListenHub 客户端 - 增强版
 * 自动生成 + 结果通知
 */

export interface Speaker {
  name: string;
  speakerId: string;
  demoAudioUrl: string;
  gender: string;
  language: string;
}

export interface PodcastEpisode {
  episodeId: string;
  createdAt: number;
  failCode: number;
  processStatus: 'pending' | 'processing' | 'success' | 'failed';
  credits: number;
  title: string;
  outline: string;
  cover: string;
  audioUrl: string;
  scripts: Array<{
    speakerId: string;
    speakerName: string;
    content: string;
  }>;
}

export interface GenerationResult {
  success: boolean;
  episodeId: string;
  title?: string;
  audioUrl?: string;
  cover?: string;
  credits?: number;
  error?: string;
}

export class ListenHubClient {
  private apiKey: string;
  private baseUrl: string;
  private onProgress?: (status: string, episodeId: string) => void;
  private onComplete?: (result: GenerationResult) => void;

  constructor(
    apiKey: string, 
    baseUrl = 'https://api.marswave.ai/openapi/v1',
    callbacks?: {
      onProgress?: (status: string, episodeId: string) => void;
      onComplete?: (result: GenerationResult) => void;
    }
  ) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.onProgress = callbacks?.onProgress;
    this.onComplete = callbacks?.onComplete;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      ...((options?.headers as Record<string, string>) || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();
    
    if (data.code !== 0) {
      throw new Error(`ListenHub API error: ${data.message}`);
    }

    return data.data;
  }

  /**
   * 获取语音列表
   */
  async listSpeakers(language: string = 'zh'): Promise<Speaker[]> {
    const result = await this.request<{ items: Speaker[] }>(`/speakers/list?language=${language}`);
    return result.items;
  }

  /**
   * 创建 AI 播客
   */
  async createPodcast(params: {
    query: string;
    speakers: Array<{ speakerId: string }>;
    language: string;
    mode: 'quick' | 'standard' | 'advanced';
  }): Promise<{ episodeId: string }> {
    return this.request('/podcast/episodes', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  /**
   * 查询播客生成状态
   */
  async getPodcastStatus(episodeId: string): Promise<PodcastEpisode> {
    return this.request(`/podcast/episodes/${episodeId}`);
  }

  /**
   * 生成播客并自动等待完成（带进度回调）
   */
  async generatePodcast(params: {
    query: string;
    speakers: Array<{ speakerId: string }>;
    language: string;
    mode: 'quick' | 'standard' | 'advanced';
    timeout?: number;
    pollInterval?: number;
  }): Promise<GenerationResult> {
    try {
      // 1. 创建任务
      const { episodeId } = await this.createPodcast(params);
      console.log(`🎙️ 播客任务已创建: ${episodeId}`);
      this.onProgress?.('pending', episodeId);

      // 2. 首次等待 60 秒
      await this.sleep(60000);

      // 3. 轮询状态
      const timeout = params.timeout || 300000;
      const interval = params.pollInterval || 10000;
      const startTime = Date.now();

      while (Date.now() - startTime < timeout) {
        const episode = await this.getPodcastStatus(episodeId);
        this.onProgress?.(episode.processStatus, episodeId);

        if (episode.processStatus === 'success') {
          const result: GenerationResult = {
            success: true,
            episodeId,
            title: episode.title,
            audioUrl: episode.audioUrl,
            cover: episode.cover,
            credits: episode.credits,
          };
          this.onComplete?.(result);
          return result;
        }
        
        if (episode.processStatus === 'failed') {
          const result: GenerationResult = {
            success: false,
            episodeId,
            error: `生成失败: ${episode.failCode}`,
          };
          this.onComplete?.(result);
          return result;
        }

        await this.sleep(interval);
      }

      throw new Error('生成超时');
    } catch (error) {
      const result: GenerationResult = {
        success: false,
        episodeId: '',
        error: error instanceof Error ? error.message : '未知错误',
      };
      this.onComplete?.(result);
      return result;
    }
  }

  /**
   * 获取用户的克隆声音
   */
  async getClonedVoices(): Promise<Speaker[]> {
    const speakers = await this.listSpeakers('zh');
    return speakers.filter(s => 
      s.speakerId.includes('voice-clone') || 
      s.demoAudioUrl.includes('voice-clone')
    );
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// 格式化结果输出
export function formatResult(result: GenerationResult): string {
  if (!result.success) {
    return `❌ 生成失败: ${result.error}`;
  }

  return `
✅ 播客生成完成！

📋 任务信息：
- 任务ID: ${result.episodeId}
- 标题: ${result.title || 'N/A'}
- 消耗积分: ${result.credits || 0}

🔗 下载链接：
- 音频MP3: ${result.audioUrl || 'N/A'}
- 封面图: ${result.cover || 'N/A'}

💡 提示：
- 链接长期有效，可直接下载
- 音频可用于视频剪辑或二次创作
`.trim();
}

// 导出默认客户端实例
export const listenhub = new ListenHubClient(
  process.env.LISTENHUB_API_KEY || 'lh_sk_693430bd6ae633c0cc867331_d72d739c443d345d87dd67ad22d8051f7683b1e1b9a3e0c3'
);
