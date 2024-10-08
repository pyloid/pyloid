from src.pylon.pylon import PylonApp
from src.pylon.api import PylonAPI, Bridge
from src.pylon.tray import TrayEvent
from src.pylon.utils import is_production, get_production_path
import os

app = PylonApp("Pylon-App", single_instance=True)

if (is_production()):
    app.set_icon(os.path.join(get_production_path(), "icon.ico"))
else:
    app.set_icon("assets/icon.ico")
    app.set_tray_icon("assets/icon.ico")

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

app.run_tray()


class CustomAPI(PylonAPI):
    @Bridge(str, int, result=str)
    def echo(self, message, message2):
        print(f"메시지: {message}-{message2}")
        return f"파이썬에서 받은 메시지: {message}-{message2}"

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
        window.load_url("http://localhost:5173")
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

window.set_size(800, 600)

if (is_production()):
    window.load_file(os.path.join(get_production_path(), "file/index.html"))
else:
    window.load_file("file/index.html")

window.show_and_focus()

app.show_notification("알림", "알림 메시지")

monitors = app.get_all_monitors()

monitors[0].geometry_changed(lambda: print("geometry_changed"))
monitors[0].orientation_changed(lambda: print("orientation_changed"))
monitors[0].refresh_rate_changed(lambda: print("refresh_rate_changed"))

app.copy_to_clipboard("test")
print(app.get_clipboard_text())

app.set_clipboard_image("assets/icon.png")
print(app.get_clipboard_image())

window.add_shortcut("Ctrl+Shift+I", lambda: (print("Ctrl+Shift+I 단축키가 눌렸습니다. Ctrl+Shift+Q 단축키를 제거합니다."), window.remove_shortcut("Ctrl+Shift+Q")))
window.add_shortcut("Ctrl+Shift+Q", lambda: (print("Ctrl+Shift+Q 단축키가 눌렸습니다.")))
window.add_shortcut("Ctrl+Shift+S", lambda: (print("Ctrl+Shift+S 단축키가 눌렸습니다."), print(window.get_all_shortcuts())))

window.add_shortcut("Ctrl+Shift+E", lambda: (print("Ctrl+Shift+E 단축키가 눌렸습니다."), window.emit('pythonEvent', { "message": 'Hello from Python!' })))

app.set_auto_start(False)
print(app.is_auto_start())

app.run()