#!/usr/bin/env python3
"""测试 Scrapling 基本功能"""

# 测试 1: 基础 HTML 解析
print("=" * 50)
print("测试 1: HTML 解析功能")
print("=" * 50)

from scrapling.parser import Selector

html = """
<html>
<head><title>Test Page</title></head>
<body>
    <div class="container">
        <h1>Welcome to Scrapling</h1>
        <div class="products">
            <div class="product" data-id="1">
                <h2>Product A</h2>
                <span class="price">$29.99</span>
                <p class="desc">This is product A description</p>
            </div>
            <div class="product" data-id="2">
                <h2>Product B</h2>
                <span class="price">$49.99</span>
                <p class="desc">This is product B description</p>
            </div>
            <div class="product" data-id="3">
                <h2>Product C</h2>
                <span class="price">$19.99</span>
                <p class="desc">This is product C description</p>
            </div>
        </div>
        <a href="/next-page" class="next">Next Page →</a>
    </div>
</body>
</html>
"""

page = Selector(html)

# CSS 选择器
products = page.css('.product')
print(f"找到 {len(products)} 个产品")

for i, product in enumerate(products, 1):
    name = product.css('h2::text').get()
    price = product.css('.price::text').get()
    desc = product.css('.desc::text').get()
    product_id = product.attrib.get('data-id')
    print(f"  [{i}] ID={product_id}, 名称={name}, 价格={price}")

# XPath 选择器
print("\n使用 XPath 选择器:")
titles = page.xpath('//h2/text()').getall()
print(f"所有标题: {titles}")

# 链接提取
next_link = page.css('a.next::attr(href)').get()
print(f"\n下一页链接: {next_link}")

print("\n" + "=" * 50)
print("测试 2: 网页抓取 (Fetcher)")
print("=" * 50)

# 测试真实网页抓取 (使用 HTTP 请求，不需要浏览器)
from scrapling.fetchers import Fetcher

try:
    # 抓取 quotes.toscrape.com (经典的测试网站)
    page = Fetcher.get('http://quotes.toscrape.com/')
    quotes = page.css('.quote')
    print(f"成功抓取，找到 {len(quotes)} 条名言")
    
    # 显示前 3 条
    for quote in quotes[:3]:
        text = quote.css('.text::text').get()
        author = quote.css('.author::text').get()
        tags = quote.css('.tag::text').getall()
        print(f"  \"{text[:50]}...\" - {author}")
        print(f"    标签: {', '.join(tags)}")
except Exception as e:
    print(f"抓取失败: {e}")

print("\n" + "=" * 50)
print("测试 3: MCP 服务器检查")
print("=" * 50)

try:
    # 检查 MCP 是否可用
    from scrapling.mcp import server
    print("MCP 服务器模块已安装 ✓")
except ImportError as e:
    print(f"MCP 服务器模块不可用: {e}")

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)
