from src.pyloid.pyloid import Pyloid
from src.pyloid.utils import is_production, get_production_path
import os
from PySide6.QtWebEngineCore import QWebEngineSettings

app = Pyloid(app_name="Pyloid-App", single_instance=True)

if is_production():
    app.set_icon(os.path.join(get_production_path(), "icon.ico"))
    app.set_tray_icon(os.path.join(get_production_path(), "icon.ico"))
else:
    app.set_icon("assets/icon.ico")
    app.set_tray_icon("assets/icon.ico")

win = app.create_window("main2")


win.set_dev_tools(True)
win.set_frame(True)

if is_production():
    win.load_file(os.path.join(get_production_path(), "file/index3.html"))
else:
    win.load_file("file/index3.html")


win.show_and_focus()

from pprint import pprint

pprint(app.get_all_monitors()[0].info())

app.run()
