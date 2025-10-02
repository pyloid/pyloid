import threading
import uvicorn
from src.pyloid.pyloid import Pyloid
from fastapi import FastAPI, HTTPException
import asyncio
from src.pyloid.pyloid import TrayEvent
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import http.server
import socketserver
import os

# Pyloid 앱 생성 및 설정
app_instance = Pyloid(
	app_name='Pyloid-App', single_instance=False, data={'port': 8000}
)
app_instance.set_icon('assets/icon.png')
app_instance.set_tray_icon('assets/icon.png')

# 서빙할 디렉토리로 변경
os.chdir('file')

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler


# 다른 스레드에서 HTTP 서버 실행
def run_server():
	with socketserver.TCPServer(('', PORT), Handler) as httpd:
		print(f'서버가 포트 {PORT}에서 실행 중입니다.')
		httpd.serve_forever()


# 백그라운드 스레드 생성 및 시작
import threading

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

window = app_instance.create_window('Pyloid-App')
window.load_url('http://localhost:8000')
window.show()
window.set_dev_tools(True)

app_instance.run()
