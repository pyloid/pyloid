import threading
import uvicorn
from src.pyloid.pyloid import Pyloid
from fastapi import FastAPI, HTTPException
import asyncio
from src.pyloid.pyloid import TrayEvent

# Pyloid 앱 생성 및 설정
app_instance = Pyloid(app_name="Pyloid-App", single_instance=False, data={"port": 8000})
app_instance.set_icon("assets/icon.png")
app_instance.set_tray_icon("assets/icon.png")

window = app_instance.create_window("Pyloid-App")
window.load_file("file/index5.html")
window.show()
window.set_dev_tools(True)

from pprint import pprint

pprint(app_instance.get_all_monitors()[0].info())

print(app_instance.is_auto_start())

# FastAPI 앱 생성
api = FastAPI()

# 엔드포인트 정의
@api.get("/window/create")
async def create_window():
    await asyncio.sleep(3)
    try:
        new_window = app_instance.create_window("Pyloid-App")
        new_window.load_file("file/index2.html")
        new_window.show_and_focus()
        return {"status": "success", "window_id": new_window.get_id()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/set_tray_actions")
async def set_tray_actions():
    app_instance.set_tray_actions(
        {
            TrayEvent.DoubleClick: lambda: print("Tray icon was double-clicked."),
            TrayEvent.MiddleClick: lambda: print("Tray icon was middle-clicked."),
            TrayEvent.RightClick: lambda: print("Tray icon was right-clicked."),
            TrayEvent.LeftClick: lambda: print("Tray icon was left-clicked."),
        }
    )
    return {"status": "success"}

def run_api():
    uvicorn.run(api, host="127.0.0.1", port=app_instance.data["port"])

if __name__ == "__main__":
    # FastAPI 서버를 별도의 스레드에서 실행
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Pyloid 앱의 이벤트 루프 실행
    app_instance.run()

