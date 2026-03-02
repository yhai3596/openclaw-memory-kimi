#!/usr/bin/env python3
"""
ListenHub API 测试脚本
测试 API Key 是否有效
"""

import requests
import json

API_KEY = "lh_sk_693430bd6ae633c0cc867331_d72d739c443d345d87dd67ad22d8051f7683b1e1b9a3e0c3"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 尝试不同的 API 端点
endpoints = [
    "https://api.listenhub.ai/v1/podcasts",
    "https://api.listenhub.ai/v1/audio",
    "https://api.listenhub.ai/v1/generate",
    "https://listenhub.ai/api/v1/podcasts",
    "https://api.listenhub.ai/podcasts",
]

print("测试 ListenHub API 端点...")
print("=" * 50)

for url in endpoints:
    print(f"\n测试: {url}")
    try:
        # 尝试 GET 请求
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"  GET 状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"  GET 错误: {e}")
    
    try:
        # 尝试 POST 请求（创建播客）
        payload = {
            "topic": "测试播客",
            "style": "dialogue"
        }
        response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        print(f"  POST 状态码: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"  响应: {response.text[:200]}")
            print("  ✅ 找到正确的 API 端点！")
            break
    except Exception as e:
        print(f"  POST 错误: {e}")

print("\n" + "=" * 50)
print("测试完成")
