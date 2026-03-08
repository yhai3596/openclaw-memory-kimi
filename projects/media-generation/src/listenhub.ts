/**
 * ListenHub API 客户端
 * 文档: https://listenhub.ai/docs/en/openapi
 * Base URL: https://api.marswave.ai/openapi/v1
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

export class ListenHubClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl = 'https://api.marswave.ai/openapi/v1') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
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
   * 轮询等待播客生成完成
   */
  async waitForPodcast(
    episodeId: string,
    options: { timeout?: number; interval?: number } = {}
  ): Promise<PodcastEpisode> {
    const { timeout = 300000, interval = 10000 } = options;
    const startTime = Date.now();

    // 首次等待 60 秒
    await new Promise(resolve => setTimeout(resolve, 60000));

    while (Date.now() - startTime < timeout) {
      const episode = await this.getPodcastStatus(episodeId);
      
      if (episode.processStatus === 'success') {
        return episode;
      }
      
      if (episode.processStatus === 'failed') {
        throw new Error(`Podcast generation failed: ${episode.failCode}`);
      }

      await new Promise(resolve => setTimeout(resolve, interval));
    }

    throw new Error('Podcast generation timeout');
  }
}

// 导出单例（使用环境变量中的 API Key）
export const listenhub = new ListenHubClient(
  process.env.LISTENHUB_API_KEY || 'lh_sk_693430bd6ae633c0cc867331_d72d739c443d345d87dd67ad22d8051f7683b1e1b9a3e0c3'
);
