from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEnginePermission
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from typing import Any


class CustomWebPage(QWebEnginePage):
    def __init__(self, profile=None):
        super().__init__(profile)
        self.permissionRequested.connect(self._handlePermissionRequest)
        self.desktopMediaRequested.connect(self._handleDesktopMediaRequest)

    def _handlePermissionRequest(self, permission: QWebEnginePermission):     
        permission.grant() # Allow all permissions by default
        
    # This is a desktop media request
    # But TypeError: cannot be converted
    def _handleDesktopMediaRequest(self, request: Any):
        print("Desktop media request received:", request)


class CustomWebEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.custom_page = CustomWebPage()
        self.setPage(self.custom_page)
        
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True
        )



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.web_view = CustomWebEngineView()
        self.setCentralWidget(self.web_view)
        
        html_content = """
        <html>
            <head><title>Custom Page</title></head>
            <style>
                video {
                    width: 400px;
                    height: 275px;
                    margin: 10px;
                }
                button {
                    margin: 5px;
                    padding: 10px;
                }
            </style>
            <body>
                <h1>WebRTC Media Test</h1>
                <video id="localVideo" autoplay playsinline></video>
                <br />
                <button id="startButton">Start Screen Capture</button>
                <script>
                    const localVideo = document.getElementById('localVideo');
                    const startButton = document.getElementById('startButton');
                    let stream;

                    startButton.addEventListener('click', async () => {
                        stream = await navigator.mediaDevices.getDisplayMedia({
                            video: true,
                        });
                        localVideo.srcObject = stream;
                    });
                </script>
            </body>
        </html>
        """
        
        self.web_view.setHtml(html_content, QUrl("http://localhost"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())