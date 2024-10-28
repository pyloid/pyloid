from src.pyloid.pyloid import Pyloid
from src.pyloid.api import PyloidAPI, Bridge
from src.pyloid.tray import TrayEvent
from src.pyloid.utils import is_production, get_production_path
from src.pyloid.timer import PyloidTimer
import os

from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QMovie
from PySide6.QtWidgets import QSplashScreen, QLabel
from PySide6.QtWidgets import QWidget, QVBoxLayout


class CustomAPI(PyloidAPI):
    @Bridge(result=str)
    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(filter="Text files (*.txt)")
        return file if file else ""

    @Bridge(result=str)
    def save_file(self):
        file, _ = QFileDialog.getSaveFileName(filter="Text files (*.txt)")
        return file if file else ""

    @Bridge(result=str)
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory()
        return directory if directory else ""


class MessageAPI(PyloidAPI):
    @Bridge(str, str, result=str)
    def show_info(self, title: str, message: str):
        QMessageBox.information(None, title, message)

    @Bridge(str, str, result=str)
    def show_warning(self, title: str, message: str):
        QMessageBox.warning(None, title, message)

    @Bridge(str, str, result=bool)
    def show_question(self, title: str, message: str):
        reply = QMessageBox.question(None, title, message)
        return reply == QMessageBox.Yes


app = Pyloid(app_name="Pyloid-App", single_instance=True)


window = app.create_window(
    title="Custom API Example", js_apis=[CustomAPI(), MessageAPI()]
)
window.set_gif_splash_screen(
    "./assets/loading.gif", close_on_load=False, position="bottom-right"
)

window.set_position_by_anchor("bottom-right")

# window.load_url("file:///file/index4.html")
window.load_html(
    """
    <html>
    <body>
    <h1>Hello, Pyloid!</h1>
    </body>
    </html>
    """
)


from PySide6.QtCore import QThread
import time


class SplashWorkerThread(QThread):
    def run(self):
        time.sleep(2)  # 2초 동안 작업 시뮬레이션


def finish_callback():
    window.close_splash_screen()
    window.show_and_focus()


splash_worker = SplashWorkerThread()
splash_worker.finished.connect(finish_callback)
splash_worker.start()


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
