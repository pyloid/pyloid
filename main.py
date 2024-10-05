from src.pylon.pylon import PylonApp
from src.pylon.api import PylonAPI, Bridge
from src.pylon.tray import TrayEvent
import time


app = PylonApp(single_instance=True)

app.set_icon("assets/icon.ico")

app.set_tray_actions(
    {
        TrayEvent.DoubleClick: lambda: print("트레이 아이콘이 더블클릭되었습니다."),
        TrayEvent.MiddleClick: lambda: print("트레이 아이콘이 중간 버튼으로 클릭되었습니다."),
        TrayEvent.RightClick: lambda: print("트레이 아이콘이 오른쪽 버튼으로 클릭되었습니다."),
        TrayEvent.LeftClick: lambda: print("트레이 아이콘이 왼쪽 버튼으로 클릭되었습니다."),
    }
)

app.set_tray_menu_items(
    [
        {"label": "창 보이기", "callback": lambda: app.show_and_focus_main_window()},
        {"label": "종료", "callback": lambda: app.quit()},
    ]
)

app.setup_tray()

class CustomAPI(PylonAPI):
    @Bridge(str, int, result=str)
    def echo(self, message, message2):
        print(type(message), type(message2))
        return f"파이썬에서 받은 메시지: {message}, {message2}"

    @Bridge(result=str)
    def getAppVersion(self):
        return "1.0.0"

    @Bridge(result=str)
    def create_window(self):
        window = app.create_window(
            title="Pylon Browser2",
            frame=True,
            context_menu=False,
            js_apis=[CustomAPI()],
            dev_tools=True
        )

        
        window.set_size(800, 600)
        window.set_position(0, 0)
        window.load_url("https://www.google.com")
        window.show()
        window.focus()

        return window.id


window = app.create_window(
    title="Pylon Browser1",
    frame=True,
    context_menu=False,
    js_apis=[CustomAPI()],
    dev_tools=True
)

window.set_size(1500, 1000)

window.load_file("file/index.html")
window.show_and_focus()

app.run()
