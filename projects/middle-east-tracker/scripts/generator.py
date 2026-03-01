#!/usr/bin/env python3
"""
生成时间线网页
"""

import json
from datetime import datetime
from pathlib import Path

def generate_timeline():
    data_dir = Path(__file__).parent.parent / "data"
    web_dir = Path(__file__).parent.parent / "web"
    web_dir.mkdir(exist_ok=True)
    
    # 读取今天的新闻
    today = datetime.now().strftime("%Y-%m-%d")
    news_file = data_dir / f"news-{today}.json"
    
    if not news_file.exists():
        news = []
    else:
        with open(news_file) as f:
            news = json.load(f)
    
    # 按类别分组
    categories = {"军事": [], "政治": [], "经济": [], "人道": [], "其他": []}
    for item in news:
        cat = item.get("category", "其他")
        categories[cat].append(item)
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中东局势实时追踪 | {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: #f5f5f5; }}
        .header {{ background: #1a1a2e; color: white; padding: 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .stats {{ display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }}
        .stat-box {{ background: white; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }}
        .stat-box .number {{ font-size: 24px; font-weight: bold; color: #e74c3c; }}
        .timeline {{ position: relative; padding-left: 30px; }}
        .timeline::before {{ content: ''; position: absolute; left: 10px; top: 0; bottom: 0; width: 2px; background: #ddd; }}
        .event {{ background: white; margin-bottom: 15px; padding: 15px; border-radius: 8px; }}
        .event-time {{ font-size: 12px; color: #888; }}
        .event-title {{ font-size: 16px; font-weight: bold; margin: 5px 0; }}
        .event-source {{ font-size: 12px; color: #3498db; }}
        .category-tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 5px; color: white; }}
        .cat-军事 {{ background: #e74c3c; }}
        .cat-政治 {{ background: #3498db; }}
        .cat-经济 {{ background: #27ae60; }}
        .cat-人道 {{ background: #f39c12; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔴 中东局势实时追踪</h1>
        <div>美伊冲突动态 · 自动更新 · 多源验证</div>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat-box"><div class="number">{len(news)}</div><div>今日事件</div></div>
            <div class="stat-box"><div class="number">{len(categories['军事'])}</div><div>军事动态</div></div>
            <div class="stat-box"><div class="number">{len(categories['政治'])}</div><div>政治进展</div></div>
            <div class="stat-box"><div class="number">{len(categories['人道'])}</div><div>人道状况</div></div>
        </div>
        <div class="timeline">
"""
    
    for item in news[:50]:
        time_str = item["timestamp"][11:16] if len(item["timestamp"]) > 16 else item["timestamp"]
        cat = item.get("category", "其他")
        html += f"""
            <div class="event">
                <div class="event-time">{time_str}</div>
                <div class="event-title">
                    <span class="category-tag cat-{cat}">{cat}</span>
                    {item['title']}
                </div>
                <div>{item['content'][:150]}...</div>
                <div class="event-source">来源: <a href="{item['source_url']}" target="_blank">{item['source']}</a></div>
            </div>
"""
    
    if not news:
        html += '<div class="event"><div class="event-title">暂无数据</div><div>正在抓取最新信息...</div></div>'
    
    html += """
        </div>
    </div>
    <div class="footer">
        <p>数据来源: 新华社、新华网、21世纪经济报道等</p>
        <p>自动更新 · 每10分钟刷新</p>
    </div>
</body>
</html>
"""
    
    # 保存
    output_file = web_dir / "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"网页已生成: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_timeline()
