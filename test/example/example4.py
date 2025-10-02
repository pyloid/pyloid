import sys
from PySide6.QtWidgets import (
	QApplication,
)
from PySide6.QtWebEngineWidgets import (
	QWebEngineView,
)

html = """
<!DOCTYPE html>
<html>
  <body>
    <h3>IME Test</h3>
    <textarea rows="5" cols="50" placeholder="Type in Korean here..."></textarea>
  </body>
</html>
"""

app = QApplication(
	sys.argv
)
view = QWebEngineView()
view.setHtml(
	html
)
view.resize(
	800,
	600,
)
view.show()
sys.exit(
	app.exec()
)
