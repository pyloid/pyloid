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

print(app.open_file_dialog())
print(app.save_file_dialog())
print(app.select_directory_dialog())

# timer = PyloidTimer()
# timer.start_precise_periodic_timer(1000, lambda: print("1000ms"))
# timer.start_coarse_periodic_timer(2000, lambda: print("2000ms"))


app.run()
