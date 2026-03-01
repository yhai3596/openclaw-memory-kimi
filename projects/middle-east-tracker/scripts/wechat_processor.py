#!/usr/bin/env python3
"""
公众号文章处理器
接收转发的公众号文章，提取信息，更新时间线
"""

import json
import re
from datetime import datetime
from pathlib import Path

class WechatArticleProcessor:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    def process_article(self, title, content, source, url=""):
        """处理单篇文章"""
        
        # 生成 ID
        article_id = f"wx_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 提取关键信息
        article = {
            "id": article_id,
            "timestamp": datetime.now().isoformat(),
            "title": title.strip(),
            "content": content[:500] if len(content) > 500 else content,
            "source": source,
            "source_url": url,
            "category": self._classify(title, content),
            "verified": source in ["人民日报", "新华社", "新华网", "央视新闻"]
        }
        
        # 保存
        self._save_article(article)
        
        return article
    
    def _classify(self, title, content):
        """分类"""
        text = f"{title} {content}".lower()
        
        if any(w in text for w in ["导弹", "袭击", "军事", "军队", "国防", "战争", "冲突"]):
            return "军事"
        elif any(w in text for w in ["总统", "领袖", "政府", "外交", "联合国", "声明"]):
            return "政治"
        elif any(w in text for w in ["油价", "经济", "市场", "股票", "贸易", "金融"]):
            return "经济"
        elif any(w in text for w in ["死亡", "伤亡", "平民", "医院", "学校", "人道"]):
            return "人道"
        else:
            return "其他"
    
    def _save_article(self, article):
        """保存文章"""
        today = datetime.now().strftime("%Y-%m-%d")
        news_file = self.data_dir / f"news-{today}.json"
        
        # 读取已有数据
        existing = []
        if news_file.exists():
            with open(news_file) as f:
                existing = json.load(f)
        
        # 检查是否已存在（相同标题）
        existing_titles = {n["title"] for n in existing}
        if article["title"] in existing_titles:
            print(f"文章已存在: {article['title'][:30]}...")
            return
        
        # 添加新文章
        existing.insert(0, article)
        
        # 保存
        with open(news_file, "w") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f"已保存文章: {article['title'][:30]}...")
    
    def get_stats(self):
        """获取统计"""
        all_news = []
        for news_file in self.data_dir.glob("news-*.json"):
            try:
                with open(news_file) as f:
                    all_news.extend(json.load(f))
            except:
                continue
        
        return {
            "total": len(all_news),
            "today": len([n for n in all_news if n["timestamp"][:10] == datetime.now().strftime("%Y-%m-%d")])
        }

if __name__ == "__main__":
    processor = WechatArticleProcessor()
    
    # 测试
    test_article = processor.process_article(
        title="测试文章：伊朗最新局势",
        content="这是一篇测试文章的内容...",
        source="人民日报",
        url="https://mp.weixin.qq.com/xxx"
    )
    
    print(json.dumps(test_article, ensure_ascii=False, indent=2))
    print(f"统计: {processor.get_stats()}")
