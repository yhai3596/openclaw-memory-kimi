# 中东局势实时追踪系统

## 项目目标
实时追踪美伊冲突动态，生成时间线，自动更新网站

## 信息源配置

### 主要来源（RSS）
- 新华社: http://www.xinhuanet.com/rss/
- 新华网: http://www.news.cn/rss/
- 人民日报: http://paper.people.com.cn/rss/
- 央视新闻: https://content.cctv.com/rss/
- 21世纪经济报道: https://m.21jingji.com/rss/

### 备用来源（网页抓取）
- 新浪新闻: https://news.sina.com.cn/world/
- 腾讯新闻: https://new.qq.com/ch/world/
- 网易新闻: https://news.163.com/world/

## 更新频率配置
```yaml
fetch_interval: 600  # 默认10分钟（秒）
max_interval: 3600   # 最大1小时
min_interval: 300    # 最小5分钟
failover_threshold: 3  # 连续失败3次切换源
```

## 容错机制
1. **源级容错**: 单个源失败自动切换备用源
2. **方法容错**: RSS失败→网页抓取→社交媒体
3. **内容去重**: 相同事件合并，保留最早来源

## 数据格式
```json
{
  "id": "uuid",
  "timestamp": "2026-03-01T12:00:00+08:00",
  "title": "事件标题",
  "content": "事件内容",
  "source": "新华社",
  "source_url": "https://...",
  "category": "军事/政治/经济/人道",
  "location": "德黑兰",
  "verified": false
}
```

## 展示要求
- 每条信息必须显示来源
- 未核实信息标注"待确认"
- 时间线倒序排列
- 支持按类别筛选
