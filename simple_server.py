#!/usr/bin/env python3
"""
Simple Local HTTP Server để serve dashboard HTML
Giải quyết vấn đề CORS khi load file JSON local
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Cấu hình
PORT = 8000
DIRECTORY = Path(__file__).parent.absolute()

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, format, *args):
        # Tùy chỉnh log messages
        print(f"[{self.client_address[0]}] {format % args}")

def start_server():
    """Khởi động server"""
    handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════════╗
║           DASHBOARD LOCAL SERVER STARTED                   ║
╚════════════════════════════════════════════════════════════╝

📍 Server Address: http://localhost:{PORT}
📁 Serving from:   {DIRECTORY}

🌐 Dashboard URL:  http://localhost:{PORT}/index2_1.html

✅ Server is running... (Press Ctrl+C to stop)
        """)
        
        # Mở browser tự động
        try:
            webbrowser.open(f"http://localhost:{PORT}/index2_1.html")
            print("🚀 Mở trình duyệt tự động...")
        except:
            print(f"⚠️  Mở trình duyệt thủ công: http://localhost:{PORT}/index2_1.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✋ Server stopped by user")
            print("Thank you for using Dashboard Server!")

if __name__ == "__main__":
    start_server()
