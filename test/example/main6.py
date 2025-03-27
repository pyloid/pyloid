from pyloid.pyloid import Pyloid
from pyloid.utils import is_production, get_production_path
import os

app = Pyloid(app_name="Pyloid-App", single_instance=True)

if is_production():
    app.set_icon(os.path.join(get_production_path(), "icon.ico"))
    app.set_tray_icon(os.path.join(get_production_path(), "icon.ico"))
else:
    app.set_icon("assets/icon.ico")
    app.set_tray_icon("assets/icon.ico")

win = app.create_window("main2")


win.set_dev_tools(True)

if is_production():
    win.load_file(os.path.join(get_production_path(), "file/index6.html"))
else:
    win.load_file("file/index6.html")

win.show_and_focus()


from PySide6.QtCore import QThread, Signal
import time

class ProgressWorkerThread(QThread):
    progress = Signal(int)

    def run(self):
        for i in range(101):
            self.progress.emit(i)
            time.sleep(0.1)  # 작업 시뮬레이션

# 사용 예시
progress_worker = ProgressWorkerThread()
progress_worker.progress.connect(lambda v: print(f"진행률: {v}%"))
progress_worker.finished.connect(lambda: print("작업 완료!"))
progress_worker.start()

app.run()