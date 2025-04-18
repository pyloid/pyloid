from src.pyloid.api import PyloidAPI, Bridge
from src.pyloid.pyloid import _Pyloid
from src.pyloid.utils import is_production, get_production_path
import os
from src.pyloid.pyloid import TrayEvent

app = _Pyloid(app_name="Pyloid-App", single_instance=False)

if is_production():
    app.set_icon(os.path.join(get_production_path(), "icon.ico"))
    app.set_tray_icon(os.path.join(get_production_path(), "icon.ico"))
else:
    app.set_icon("assets/icon.ico")
    app.set_tray_icon("assets/icon.ico")

app.set_tray_actions(
    {
        TrayEvent.DoubleClick: lambda: print("Tray icon was double-clicked."),
        TrayEvent.MiddleClick: lambda: print("Tray icon was middle-clicked."),
        TrayEvent.RightClick: lambda: print("Tray icon was right-clicked."),
        TrayEvent.LeftClick: lambda: print("Tray icon was left-clicked."),
    }
)

class customAPI(PyloidAPI):
    @Bridge(result=str)
    def create_window(self):
        window = app.create_window(
            title="Pyloid Browser2",
            frame=True,
            context_menu=False,
            js_apis=[customAPI()],
            dev_tools=True,
        )

        window.set_size(800, 600)
        window.set_position(0, 0)
        window.load_file("file/index2.html")
        window.show()
        window.focus()

        return window.id

    @Bridge()
    def customClose(self):
        if len(self.app.get_windows()) > 1:
            self.window.close()
        else:
            self.window.hide()


win = app.create_window("Pyloid", js_apis=[customAPI()])


win.set_dev_tools(True)
win.set_frame(True)
# win.set_context_menu(True)

if is_production():
    win.load_file(os.path.join(get_production_path(), "file/index5.html"))
else:
    win.load_file("file/index5.html")


win.show_and_focus()
from pprint import pprint

pprint(app.get_all_monitors()[0].info())

app.run()
