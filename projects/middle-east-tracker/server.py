#!/usr/bin/env python3
"""
简易 Web 服务器 - 用于公网访问时间线网页
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
WEB_DIR = Path(__file__).parent.parent / "web"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    
    def log_message(self, format, *args):
        # 简化日志
        print(f"[{self.log_date_time_string()}] {args[0]}")

if __name__ == "__main__":
    os.chdir(WEB_DIR)
    
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"=== 中东局势追踪网站已启动 ===")
        print(f"访问地址: http://115.191.53.127:{PORT}")
        print(f"本地测试: http://localhost:{PORT}")
        print(f"按 Ctrl+C 停止")
        print("")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
