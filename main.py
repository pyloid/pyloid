from src.pylon.pylon import PylonApp, get_resource_path, is_production
from src.pylon.api import PylonAPI, Bridge
from src.pylon.tray import TrayEvent


app = PylonApp(single_instance=True, icon_path="assets/icon.ico")


def on_double_click():
    print("트레이 아이콘이 더블클릭되었습니다.")


def on_middle_click():
    print("트레이 아이콘이 중간 버튼으로 클릭되었습니다.")


app.set_tray_actions(
    {
        TrayEvent.DoubleClick: on_double_click,
        TrayEvent.MiddleClick: on_middle_click,
    }
)


def show_main_window():
    app.show_main_window()


app.set_tray_menu_items(
    [
        {"label": "창 보이기", "callback": show_main_window},
        {"label": "종료", "callback": app.quit},
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
            "file/index.html",
            title="Pylon Browser4",
            frame=True,
            context_menu=False,
            js_apis=[CustomAPI()],
            enable_dev_tools=True,
            width=1200,
            height=800,
            x=100,
            y=100,
        )
        return window.id


window = app.create_window(
    "file/index.html",
    title="Pylon Browser1",
    frame=True,
    context_menu=False,
    js_apis=[CustomAPI()],
    enable_dev_tools=True,
    width=1200,
    height=800,
    x=300,
    y=300,
)


app.run()
