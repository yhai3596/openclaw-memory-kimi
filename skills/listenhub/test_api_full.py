#!/usr/bin/env python3
"""
ListenHub API 完整测试
尝试各种可能的端点组合
"""

import requests
import json

API_KEY = "lh_sk_693430bd6ae633c0cc867331_d72d739c443d345d87dd67ad22d8051f7683b1e1b9a3e0c3"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 扩展测试端点
base_urls = [
    "https://api.listenhub.ai",
    "https://listenhub.ai/api",
    "https://api.listenhub.ai/api",
]

paths = [
    "/v1/podcasts",
    "/v1/audio",
    "/v1/videos",
    "/v1/generate",
    "/podcasts",
    "/audio",
    "/generate",
    "/skills/podcast",
    "/skills/audio",
]

print("完整 API 端点扫描...")
print("=" * 60)

working_endpoints = []

for base in base_urls:
    for path in paths:
        url = f"{base}{path}"
        print(f"\n测试: {url}")
        
        # POST 测试
        try:
            payload = {"topic": "测试", "content": "测试内容"}
            response = requests.post(url, headers=HEADERS, json=payload, timeout=5)
            print(f"  POST: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                print(f"  ✅ 找到可用端点!")
                print(f"  响应: {response.text[:300]}")
                working_endpoints.append(("POST", url, response.status_code))
            elif response.status_code == 400:
                print(f"  🟡 端点存在但参数错误")
                working_endpoints.append(("POST", url, response.status_code))
            elif response.status_code == 401:
                print(f"  🔴 认证失败，检查 API Key")
            elif response.status_code == 405:
                print(f"  🟡 方法不允许，尝试 GET")
                # 尝试 GET
                try:
                    get_resp = requests.get(url, headers=HEADERS, timeout=5)
                    print(f"  GET: {get_resp.status_code}")
                    if get_resp.status_code == 200:
                        working_endpoints.append(("GET", url, get_resp.status_code))
                except:
                    pass
        except requests.exceptions.Timeout:
            print(f"  ⏱️ 超时")
        except Exception as e:
            print(f"  ❌ {str(e)[:50]}")

print("\n" + "=" * 60)
print("可用端点汇总:")
for method, url, code in working_endpoints:
    print(f"  {method} {url} -> {code}")

if not working_endpoints:
    print("  未找到可用端点，可能需要:")
    print("  1. 检查 API Key 是否正确")
    print("  2. 联系 support@marswave.ai 获取正确端点")
    print("  3. 确认账户是否已激活 API 权限")
