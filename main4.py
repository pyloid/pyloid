from src.pyloid.pyloid import Pyloid
from src.pyloid.api import PyloidAPI, Bridge
from src.pyloid.tray import TrayEvent
from src.pyloid.utils import is_production, get_production_path
from src.pyloid.timer import PyloidTimer
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
import os

app = Pyloid(app_name="Pyloid-App", single_instance=True)

# Create the WebEngine view and page
view = QWebEngineView()
page = view.page()

# Connect to the featurePermissionRequested signal to handle permission requests
def on_feature_permission_requested(url, feature):
    print(feature)
    if feature in (
        QWebEnginePage.MediaAudioCapture,
        QWebEnginePage.MediaVideoCapture,
        QWebEnginePage.MediaAudioVideoCapture
    ):
        # Grant permission for audio and video capture (microphone and camera)
        page.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
    else:
        # Deny other permissions by default
        page.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)

# Connect the signal to the handler
page.featurePermissionRequested.connect(on_feature_permission_requested)

win = app.create_window("main2")

# WebRTC 관련 설정 (공개 인터페이스만 사용하지 않도록 설정)
win.set_web_engine_view_attribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, False)

# 클립보드 및 화면캡처 관련 설정들
win.set_web_engine_view_attribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
win.set_web_engine_view_attribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
win.set_web_engine_view_attribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)  # 화면 캡처 권한
win.set_dev_tools(True)

win.load_file("file/index5.html")

win.show_and_focus()

print(win.is_web_engine_view_attribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard))

print(app.get_primary_monitor().info())

app.run()
