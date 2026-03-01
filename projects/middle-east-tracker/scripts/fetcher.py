#!/usr/bin/env python3
"""
中东局势新闻抓取器
支持 RSS 和网页抓取，多源容错
"""

import json
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

class NewsFetcher:
    def __init__(self, config_file=None):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 配置
        self.config = {
            "fetch_interval": 600,  # 10分钟
            "keywords": ["伊朗", "以色列", "美国", "中东", "哈梅内伊", "特朗普", "战争", "导弹", "袭击"],
            "sources": {
                "rss": [
                    {"name": "新华社", "url": "http://www.xinhuanet.com/rss/world.xml", "enabled": True},
                    {"name": "新华网", "url": "http://www.news.cn/rss/world.xml", "enabled": True},
                    {"name": "21财经", "url": "https://m.21jingji.com/rss/world.xml", "enabled": True},
                ],
                "web": [
                    {"name": "新浪新闻", "url": "https://news.sina.com.cn/world/", "enabled": False},
                ]
            }
        }
        
        # 已抓取记录
        self.seen_file = self.data_dir / "seen.json"
        self.seen = self._load_seen()
    
    def _load_seen(self):
        """加载已抓取的URL记录"""
        if self.seen_file.exists():
            with open(self.seen_file) as f:
                return set(json.load(f))
        return set()
    
    def _save_seen(self):
        """保存已抓取记录"""
        with open(self.seen_file, "w") as f:
            json.dump(list(self.seen), f)
    
    def _generate_id(self, title, source):
        """生成唯一ID"""
        return hashlib.md5(f"{title}:{source}".encode()).hexdigest()[:12]
    
    def _is_relevant(self, title, content=""):
        """判断内容是否相关"""
        text = f"{title} {content}".lower()
        return any(kw in text for kw in self.config["keywords"])
    
    def fetch_rss(self, source_name, url):
        """抓取 RSS 源"""
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
            })
            response.encoding = "utf-8"
            
            root = ET.fromstring(response.content)
            items = []
            
            # 处理 RSS 2.0 和 Atom 格式
            for item in root.findall(".//item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                pub_date = item.findtext("pubDate", item.findtext("dc:date", ""))
                description = item.findtext("description", "").strip()
                
                if not title or not link:
                    continue
                
                # 检查是否已抓取
                item_id = self._generate_id(title, source_name)
                if item_id in self.seen:
                    continue
                
                # 检查相关性
                if not self._is_relevant(title, description):
                    continue
                
                items.append({
                    "id": item_id,
                    "timestamp": datetime.now().isoformat(),
                    "title": title,
                    "content": description[:500] if description else title,
                    "source": source_name,
                    "source_url": link,
                    "category": self._classify(title, description),
                    "verified": source_name in ["新华社", "新华网", "人民日报"]
                })
                
                self.seen.add(item_id)
            
            return items
            
        except Exception as e:
            print(f"RSS 抓取失败 {source_name}: {e}")
            return []
    
    def _classify(self, title, content):
        """简单分类"""
        text = f"{title} {content}".lower()
        
        if any(w in text for w in ["导弹", "袭击", "军事", "军队", "国防"]):
            return "军事"
        elif any(w in text for w in ["总统", "领袖", "政府", "外交", "联合国"]):
            return "政治"
        elif any(w in text for w in ["油价", "经济", "市场", "股票", "贸易"]):
            return "经济"
        elif any(w in text for w in ["死亡", "伤亡", "平民", "医院", "学校"]):
            return "人道"
        else:
            return "其他"
    
    def fetch_all(self):
        """抓取所有源"""
        all_news = []
        
        # RSS 源
        for source in self.config["sources"]["rss"]:
            if source["enabled"]:
                print(f"抓取 {source['name']}...")
                news = self.fetch_rss(source["name"], source["url"])
                all_news.extend(news)
                time.sleep(1)  # 礼貌间隔
        
        # 保存记录
        self._save_seen()
        
        # 按时间排序
        all_news.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return all_news
    
    def save_news(self, news_list):
        """保存新闻到文件"""
        today = datetime.now().strftime("%Y-%m-%d")
        news_file = self.data_dir / f"news-{today}.json"
        
        # 读取已有数据
        existing = []
        if news_file.exists():
            with open(news_file) as f:
                existing = json.load(f)
        
        # 合并去重
        existing_ids = {n["id"] for n in existing}
        new_items = [n for n in news_list if n["id"] not in existing_ids]
        
        all_items = new_items + existing
        all_items.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 保存
        with open(news_file, "w") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)
        
        return len(new_items)

if __name__ == "__main__":
    fetcher = NewsFetcher()
    print(f"开始抓取: {datetime.now()}")
    
    news = fetcher.fetch_all()
    if news:
        count = fetcher.save_news(news)
        print(f"新增 {count} 条新闻")
        for n in news[:3]:
            print(f"  [{n['source']}] {n['title'][:50]}...")
    else:
        print("暂无新新闻")
