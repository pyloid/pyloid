from src.pyloid.pyloid import Pyloid
from src.pyloid.api import PyloidAPI, Bridge
from src.pyloid.tray import TrayEvent
from src.pyloid.utils import is_production, get_production_path
from src.pyloid.timer import PyloidTimer
import os

app = Pyloid(app_name="Pyloid-App", single_instance=True)

win = app.create_window("main2")
win.load_url("https://www.example.com")
win.show_and_focus()

app.run()
