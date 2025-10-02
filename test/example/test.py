from PySide6.QtWidgets import (
	QApplication,
	QMainWindow,
)
from PySide6.QtWebEngineWidgets import (
	QWebEngineView,
)
from PySide6.QtCore import (
	Qt,
)
from PySide6.QtGui import (
	QColor,
)

html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
        }
        #main {
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 255, 0.7);
            border-radius: 100px;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <div id="main">
        <h1>둥근 모서리의 HTML 창</h1>
        <p>PySide6 + QWebEngineView 예제</p>
    </div>
</body>
</html>
"""


class MainWindow(QMainWindow):
	def __init__(
		self,
	):
		super().__init__()
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.resize(
			600,
			400,
		)

		view = QWebEngineView()
		view.page().setBackgroundColor(Qt.transparent)
		view.setHtml(html)
		self.setCentralWidget(view)


if __name__ == '__main__':
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()
