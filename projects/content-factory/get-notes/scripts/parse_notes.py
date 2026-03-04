#!/usr/bin/env python3
"""
Get 笔记 HTML 解析器
提取标题、时间、标签、正文内容
"""

import os
import re
import json
import glob
from pathlib import Path
from bs4 import BeautifulSoup

def parse_get_note(html_path):
    """解析单个 Get 笔记 HTML 文件"""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 提取标题
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else ''
    
    # 提取创建时间
    created = ''
    note_div = soup.find('div', class_='note')
    if note_div:
        for p in note_div.find_all('p'):
            text = p.get_text(strip=True)
            if text.startswith('创建于：'):
                created = text.replace('创建于：', '').strip()
                break
    
    # 提取标签
    tags = []
    tag_spans = soup.find_all('span', class_='tag')
    for tag in tag_spans:
        tags.append(tag.get_text(strip=True))
    
    # 提取正文内容
    content = ''
    content_div = soup.find('div', class_='note')
    if content_div:
        # 找到最后一个 div，通常是正文
        divs = content_div.find_all('div')
        for div in divs:
            text = div.get_text(strip=True)
            if len(text) > 50:  # 假设正文较长
                content = text
                break
        
        # 如果没找到，尝试从 p 标签提取
        if not content:
            paragraphs = content_div.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and not text.startswith('创建于：') and not text.startswith('标签：'):
                    content_parts.append(text)
            content = '\n'.join(content_parts)
    
    return {
        'title': title,
        'created': created,
        'tags': tags,
        'content': content,
        'source_file': os.path.basename(html_path)
    }

def batch_parse(input_dir, output_dir):
    """批量解析 HTML 文件"""
    html_files = glob.glob(os.path.join(input_dir, '*.html'))
    print(f"找到 {len(html_files)} 个 HTML 文件")
    
    results = []
    for html_path in html_files:
        try:
            data = parse_get_note(html_path)
            results.append(data)
            print(f"✓ {data['source_file']} - {data['title'][:30]}...")
        except Exception as e:
            print(f"✗ {os.path.basename(html_path)} - {e}")
    
    # 保存为 JSON
    output_path = os.path.join(output_dir, 'parsed_notes.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n解析完成！共 {len(results)} 条笔记")
    print(f"输出文件: {output_path}")
    
    # 生成统计
    all_tags = []
    for r in results:
        all_tags.extend(r['tags'])
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print(f"\n标签统计:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tag}: {count}")
    
    return results

if __name__ == '__main__':
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else './raw'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './parsed'
    
    os.makedirs(output_dir, exist_ok=True)
    batch_parse(input_dir, output_dir)
