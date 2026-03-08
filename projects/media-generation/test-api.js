#!/usr/bin/env node
/**
 * ListenHub API 测试脚本
 * 文档: https://listenhub.marswave.ai/docs
 */

const API_KEY = process.env.LISTENHUB_API_KEY || 'lh_sk_693430bd6ae633c0cc867331_d72d739c443d345d87dd67ad22d8051f7683b1e1b9a3e0c3';
const BASE_URL = process.env.LISTENHUB_BASE_URL || 'https://api.marswave.ai/openapi/v1';

async function testAPI() {
  console.log('🎧 ListenHub API 测试\n');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`API Key: ${API_KEY.slice(0, 20)}...\n`);

  const endpoints = [
    { name: '语音列表', path: '/speakers/list?language=zh' },
  ];

  for (const endpoint of endpoints) {
    const url = `${BASE_URL}${endpoint.path}`;
    console.log(`\n📡 测试: ${endpoint.name}`);
    console.log(`   URL: ${url}`);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
        },
      });

      const status = response.status;
      const statusText = response.statusText;
      
      if (response.ok) {
        const data = await response.json();
        console.log(`   ✅ ${status} ${statusText}`);
        console.log(`   响应: ${JSON.stringify(data, null, 2).slice(0, 200)}...`);
      } else {
        console.log(`   ❌ ${status} ${statusText}`);
        const text = await response.text();
        console.log(`   错误: ${text.slice(0, 200)}`);
      }
    } catch (error) {
      console.log(`   💥 请求失败: ${error.message}`);
    }
  }

  // 测试 TTS 生成
  console.log(`\n\n🎙️ 测试 AI 播客生成`);
  const podcastUrl = `${BASE_URL}/podcast/episodes`;
  console.log(`   URL: ${podcastUrl}`);
  
  try {
    const response = await fetch(podcastUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: '简单介绍一下人工智能的历史',
        speakers: [{ speakerId: 'chat-girl-105-cn' }],
        language: 'zh',
        mode: 'quick'
      }),
    });

    const status = response.status;
    if (response.ok) {
      const data = await response.json();
      console.log(`   ✅ ${status} - 播客任务创建成功`);
      console.log(`   任务ID: ${data.data?.episodeId || data.episodeId || 'N/A'}`);
      console.log(`   完整响应:`, JSON.stringify(data, null, 2).slice(0, 500));
    } else {
      console.log(`   ❌ ${status}`);
      const text = await response.text();
      console.log(`   错误: ${text.slice(0, 300)}`);
    }
  } catch (error) {
    console.log(`   💥 请求失败: ${error.message}`);
  }
}

testAPI();
