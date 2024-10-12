from src.pyloid.pyloid import Pyloid
from src.pyloid.api import PyloidAPI, Bridge
from src.pyloid.tray import TrayEvent
from src.pyloid.utils import is_production, get_production_path
from src.pyloid.timer import PyloidTimer
import os

app = Pyloid("Pyloid-App", single_instance=True)
timer = PyloidTimer()

if is_production():
    app.set_icon(os.path.join(get_production_path(), "icon.ico"))
else:
    app.set_icon("assets/icon.ico")
    app.set_tray_icon("assets/icon.ico")

app.set_tray_actions(
    {
        TrayEvent.DoubleClick: lambda: print("트레이 아이콘이 더블클릭되었습니다."),
        TrayEvent.MiddleClick: lambda: print(
            "트레이 아이콘이 중간 버튼으로 클릭되었습니다."
        ),
        TrayEvent.RightClick: lambda: print(
            "트레이 아이콘이 오른쪽 버튼으로 클릭되었습니다."
        ),
        TrayEvent.LeftClick: lambda: print(
            "트레이 아이콘이 왼쪽 버튼으로 클릭되었습니다."
        ),
    }
)


app.set_tray_menu_items(
    [
        {"label": "창 보이기", "callback": lambda: app.show_and_focus_main_window()},
        {"label": "종료", "callback": lambda: app.quit()},
    ]
)


class CustomAPI(PyloidAPI):
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
            title="Pyloid Browser2",
            frame=True,
            context_menu=False,
            js_apis=[CustomAPI()],
            dev_tools=True,
        )

        window.set_size(800, 600)
        window.set_position(0, 0)
        window.load_file("file/index2.html")
        window.show()
        window.focus()

        return window.id


window = app.create_window(
    title="Pyloid Browser1",
    frame=True,
    context_menu=False,
    js_apis=[CustomAPI()],
    dev_tools=True,
)

window.set_size(800, 600)

if is_production():
    window.load_file(os.path.join(get_production_path(), "file/index.html"))
else:
    window.load_file("file/index.html")

window.show_and_focus()

monitors = app.get_all_monitors()

print(monitors)

monitors[0].geometry_changed(lambda: print("geometry_changed"))
monitors[0].orientation_changed(lambda: print("orientation_changed"))
monitors[0].refresh_rate_changed(lambda: print("refresh_rate_changed"))

app.copy_to_clipboard("test")
print(app.get_clipboard_text())

app.set_clipboard_image("assets/icon.png")
print(app.get_clipboard_image())

window.add_shortcut(
    "Ctrl+Shift+I",
    lambda: (
        print("Ctrl+Shift+I 단축키가 눌렸습니다. Ctrl+Shift+Q 단축키를 제거합니다."),
        window.remove_shortcut("Ctrl+Shift+Q"),
    ),
)
window.add_shortcut(
    "Ctrl+Shift+Q", lambda: (print("Ctrl+Shift+Q 단축키가 눌렸습니다."))
)
window.add_shortcut(
    "Ctrl+Shift+S",
    lambda: (
        print("Ctrl+Shift+S 단축키가 눌렸습니다."),
        print(window.get_all_shortcuts()),
    ),
)

window.add_shortcut(
    "Ctrl+Shift+E",
    lambda: (
        print("Ctrl+Shift+E 단축키가 눌렸습니다."),
        window.emit("pythonEvent", {"message": "Hello from Python!"}),
    ),
)

app.set_auto_start(True)
print(app.is_auto_start())


# 파일 감시 시작
app.watch_file("test.txt")

# 디렉토리 감시 시작
app.watch_directory("test")


# 파일 변경 콜백 설정
def on_file_changed(path):
    print(f"파일이 변경되었습니다: {path}")


app.set_file_change_callback(on_file_changed)


# 디렉토리 변경 콜백 설정
def on_directory_changed(path):
    print(f"디렉토리가 변경되었습니다: {path}")


app.set_directory_change_callback(on_directory_changed)

# 감시 중인 경로 확인
print(app.get_watched_paths())


# 트레이 메뉴 동적 업데이트
def update_menu():
    app.set_tray_menu_items(
        [
            {
                "label": "새로운 메뉴 1",
                "callback": lambda: print("새로운 메뉴 1 클릭됨"),
            },
            {
                "label": "새로운 메뉴 2",
                "callback": lambda: print("새로운 메뉴 2 클릭됨"),
            },
            {"label": "종료", "callback": lambda: app.quit()},
        ]
    )


# 5초 후에 트레이 메뉴 업데이트
timer.start_single_shot_timer(5000, update_menu)


def update_tray_icon():
    # 트레이 아이콘 애니메이션 설정
    app.set_tray_icon_animation(
        [
            "assets/frame1.png",
            "assets/frame2.png",
            "assets/frame3.png",
            "assets/frame4.png",
        ],
        interval=500,
    )


timer.start_single_shot_timer(3000, update_tray_icon)
timer.start_single_shot_timer(6000, lambda: app.set_tray_icon("assets/icon.ico"))

# 트레이 아이콘 툴팁 설정
app.set_tray_tooltip("이것은 Pyloid 애플리케이션입니다.")

timer.start_single_shot_timer(10000, lambda: app.set_tray_tooltip("새로운 툴팁입니다!"))


# 알림 클릭 콜백 설정
def on_notification_clicked():
    print("알림이 클릭되었습니다!")


app.set_notification_callback(on_notification_clicked)


# 새로운 알림 표시 (기존 코드 수정)
app.show_notification("새 알림", "이 알림을 클릭해보세요!")

app.run()
