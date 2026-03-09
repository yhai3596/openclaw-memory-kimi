#!/usr/bin/env python3
"""测试 Scrapling 高级功能"""

import asyncio

print("=" * 60)
print("测试: 异步 Fetcher 和 Session")
print("=" * 60)

from scrapling.fetchers import FetcherSession, AsyncFetcher

# 测试 Session
async def test_session():
    async with FetcherSession(impersonate='chrome') as session:
        # 并发请求多个页面
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        
        tasks = [session.get(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for i, page in enumerate(results, 1):
            quotes = page.css('.quote')
            print(f"页面 {i}: 找到 {len(quotes)} 条名言")

# 运行异步测试
asyncio.run(test_session())

print("\n" + "=" * 60)
print("测试: 自适应解析 (Adaptive Parsing)")
print("=" * 60)

from scrapling.parser import Selector

# 原始 HTML
html_v1 = """
<div class="content">
    <div class="item" data-sku="123">
        <span class="name">Product A</span>
        <span class="cost">$10</span>
    </div>
</div>
"""

# 改版后的 HTML（结构变化）
html_v2 = """
<div class="content">
    <article class="product-item" data-sku="123">
        <h3 class="product-name">Product A</h3>
        <div class="price-tag">$10</div>
    </article>
</div>
"""

# 先保存第一个版本的选择器
page1 = Selector(html_v1)
original_element = page1.css('.item')
print(f"原始页面找到: {len(original_element)} 个元素")

# 模拟网站改版后，使用 adaptive=True
page2 = Selector(html_v2)

# 尝试使用原始选择器（应该找不到）
non_adaptive = page2.css('.item')
print(f"非自适应选择器在改版页面找到: {len(non_adaptive)} 个元素")

# 使用自适应模式（应该能找到相似元素）
try:
    adaptive = page2.css('.item', adaptive=True)
    print(f"自适应选择器在改版页面找到: {len(adaptive)} 个元素")
    if adaptive:
        print(f"  找到的元素: {adaptive[0].tag}")
except Exception as e:
    print(f"自适应模式出错: {e}")

print("\n" + "=" * 60)
print("测试: 元素相似度搜索")
print("=" * 60)

html3 = """
<div class="container">
    <div class="card" data-id="1">
        <h4>Card One</h4>
        <p>Description one</p>
    </div>
    <div class="card" data-id="2">
        <h4>Card Two</h4>
        <p>Description two</p>
    </div>
    <div class="card featured" data-id="3">
        <h4>Featured Card</h4>
        <p>Featured description</p>
    </div>
</div>
"""

page3 = Selector(html3)
first_card = page3.css('.card')[0]
print(f"第一个卡片: {first_card.css('h4::text').get()}")

# 查找相似元素
similar = first_card.find_similar()
print(f"找到 {len(similar)} 个相似元素:")
for elem in similar:
    title = elem.css('h4::text').get()
    print(f"  - {title}")

print("\n" + "=" * 60)
print("测试: 文本搜索和过滤")
print("=" * 60)

# 通过文本内容查找元素
html4 = """
<div>
    <button>Click Me</button>
    <button>Submit</button>
    <button>Cancel</button>
</div>
"""

page4 = Selector(html4)

# 通过文本查找
submit_btn = page4.find_by_text('Submit')
print(f"通过文本找到的按钮: {submit_btn.get() if submit_btn else 'Not found'}")

# 正则搜索
import re
buttons = page4.find_all('button')
for btn in buttons:
    text = btn.css('::text').get()
    if re.search(r'[A-Z][a-z]+', text):  # 匹配驼峰式文本
        print(f"匹配正则的按钮: {text}")

print("\n" + "=" * 60)
print("高级功能测试完成!")
print("=" * 60)
