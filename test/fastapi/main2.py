import threading
import uvicorn
from src.pyloid.pyloid import Pyloid
from fastapi import FastAPI, HTTPException
import asyncio
from src.pyloid.pyloid import TrayEvent
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Pyloid 앱 생성 및 설정
app_instance = Pyloid(
	app_name='Pyloid-App', single_instance=False, data={'port': 8000}
)
app_instance.set_icon('assets/icon.png')
app_instance.set_tray_icon('assets/icon.png')

# FastAPI 앱 생성
api = FastAPI()


# API 라우팅 정의
@api.get('/api/window/create')
async def create_window():
	await asyncio.sleep(3)
	try:
		new_window = app_instance.create_window('Pyloid-App')
		new_window.load_file('file/index2.html')
		new_window.show_and_focus()
		return {'status': 'success', 'window_id': new_window.get_id()}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@api.get('/api/set_tray_actions')
async def set_tray_actions():
	app_instance.set_tray_actions(
		{
			TrayEvent.DoubleClick: lambda: print(
				'Tray icon was double-clicked.'
			),
			TrayEvent.MiddleClick: lambda: print(
				'Tray icon was middle-clicked.'
			),
			TrayEvent.RightClick: lambda: print('Tray icon was right-clicked.'),
			TrayEvent.LeftClick: lambda: print('Tray icon was left-clicked.'),
		}
	)
	return {'status': 'success'}


@api.get('/')
async def get_index(response_class=HTMLResponse):
	html_file = HTMLResponse(content=Path('file/index.html').read_text())
	return html_file


# 정적 파일 마운트 (모든 API 라우팅 정의 후에 마운트)
api.mount('/', StaticFiles(directory='file'), name='file')


def run_api():
	uvicorn.run(api, host='127.0.0.1', port=app_instance.data['port'])


threading.Thread(target=run_api, daemon=True).start()

window = app_instance.create_window('Pyloid-App')
window.load_url('http://localhost:8000')
window.show()
window.set_dev_tools(True)

app_instance.run()
