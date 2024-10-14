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
        TrayEvent.DoubleClick: lambda: print("Tray icon double-clicked."),
        TrayEvent.MiddleClick: lambda: print("Tray icon middle-clicked."),
        TrayEvent.RightClick: lambda: print("Tray icon right-clicked."),
        TrayEvent.LeftClick: lambda: print("Tray icon left-clicked."),
    }
)


app.set_tray_menu_items(
    [
        {"label": "Show Window", "callback": lambda: app.show_and_focus_main_window()},
        {"label": "Exit", "callback": lambda: app.quit()},
    ]
)


class CustomAPI(PyloidAPI):
    @Bridge(str, int, result=str)
    def echo(self, message, message2):
        print(f"Message: {message}-{message2}")
        return f"Message received in Python: {message}-{message2}"

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
        print("Ctrl+Shift+I shortcut pressed. Removing Ctrl+Shift+Q shortcut."),
        window.remove_shortcut("Ctrl+Shift+Q"),
    ),
)
window.add_shortcut(
    "Ctrl+Shift+Q", lambda: (print("Ctrl+Shift+Q shortcut pressed."))
)
window.add_shortcut(
    "Ctrl+Shift+S",
    lambda: (
        print("Ctrl+Shift+S shortcut pressed."),
        print(window.get_all_shortcuts()),
    ),
)

window.add_shortcut(
    "Ctrl+Shift+E",
    lambda: (
        print("Ctrl+Shift+E shortcut pressed."),
        window.emit("pythonEvent", {"message": "Hello from Python!"}),
    ),
)

app.set_auto_start(True)
print(app.is_auto_start())


# Start file watching
app.watch_file("test.txt")

# Start directory watching
app.watch_directory("test")


# Set file change callback
def on_file_changed(path):
    print(f"File changed: {path}")


app.set_file_change_callback(on_file_changed)


# Set directory change callback
def on_directory_changed(path):
    print(f"Directory changed: {path}")


app.set_directory_change_callback(on_directory_changed)

# Check watched paths
print(app.get_watched_paths())


# Dynamic update of tray menu
def update_menu():
    app.set_tray_menu_items(
        [
            {
                "label": "New Menu 1",
                "callback": lambda: print("New Menu 1 clicked"),
            },
            {
                "label": "New Menu 2",
                "callback": lambda: print("New Menu 2 clicked"),
            },
            {"label": "Exit", "callback": lambda: app.quit()},
        ]
    )


# Update tray menu after 5 seconds
timer.start_single_shot_timer(5000, update_menu)


def update_tray_icon():
    # Set tray icon animation
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

# Set tray icon tooltip
app.set_tray_tooltip("This is a Pyloid application.")

timer.start_single_shot_timer(10000, lambda: app.set_tray_tooltip("New tooltip!"))


# Set notification click callback
def on_notification_clicked():
    print("Notification clicked!")


app.set_notification_callback(on_notification_clicked)


# Show new notification (modified existing code)
app.show_notification("New Notification", "Click this notification!")

print(window.get_window_properties())
print(window.get_id())
print(window.get_title())
print(window.get_url())
print(window.get_visible())

window.set_size(600, 400)

print(window.get_size())
print(window.get_position())

window.set_resizable(False)

# window.set_frame(False)  # 기본 프레임 제거 및 커스텀 프레임 추가
# window.set_frame(True)   # 기본 프레임으로 복원

# 커스텀 프레임의 색상과 제목 변경
window.set_custom_frame(True, title="Pylon-App", bg_color="dark", text_color="white", icon_path="assets/icon.ico")

app.run()
