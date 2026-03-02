#!/usr/bin/env python3
"""
定时任务脚本 - 客服群监控
"""

import sys
import time
sys.path.insert(0, './scripts')

from service_monitor import WeComCustomerService

def main():
    service = WeComCustomerService()
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 执行定时任务...")
    
    # 1. 检查预警
    alert_count = service.check_and_send_alerts()
    print(f"  - 预警检查完成: {alert_count} 个预警")
    
    # 2. 生成日报（如果是早上9点）
    if time.strftime('%H:%M') == '09:00':
        report = service.generate_daily_report()
        print(f"  - 日报已生成")
    
    print("  ✅ 定时任务完成")

if __name__ == "__main__":
    main()
