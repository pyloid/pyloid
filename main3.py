from src.pyloid.pyloid import Pyloid
from src.pyloid.api import PyloidAPI, Bridge
from src.pyloid.tray import TrayEvent
from src.pyloid.utils import is_production, get_production_path
from src.pyloid.timer import PyloidTimer
import os

from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QFileDialog


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

    @Bridge(str, str,result=str)
    def show_warning(self, title: str, message: str):
        QMessageBox.warning(None, title, message)

    @Bridge(str, str,result=bool)
    def show_question(self, title: str, message: str):
        reply = QMessageBox.question(None, title, message)
        return reply == QMessageBox.Yes

app = Pyloid(app_name="Pyloid-App", single_instance=True)

window = app.create_window(title="Custom API Example", js_apis=[CustomAPI(), MessageAPI()])
window.load_url("file:///file/index4.html")

window.show_and_focus()


app.run()
