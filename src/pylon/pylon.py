import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, Signal, QUrl, QObject
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from .utils import get_resource_path, is_production
from .api import PylonAPI, Bridge
import uuid
from typing import List, Optional
from PySide6.QtCore import qInstallMessageHandler

# for linux debug
os.environ['QTWEBENGINE_DICTIONARIES_PATH'] = '/'

def custom_message_handler(mode, context, message):
    if not hasattr(custom_message_handler, 'vulkan_warning_shown') and (('Failed to load vulkan' in message) or ('No Vulkan library available' in message) or ('Failed to create platform Vulkan instance' in message)):
        print('\033[93mPylon Warning: Vulkan GPU API issue detected. Switching to software backend.\033[0m')
        os.environ['QT_QUICK_BACKEND'] = 'software'
        custom_message_handler.vulkan_warning_shown = True
    if 'vulkan' not in message.lower():
        print(message)

qInstallMessageHandler(custom_message_handler)

class WindowAPI(PylonAPI):
    def __init__(self, window_id, app):
        super().__init__()
        self.window_id = window_id
        self.app = app

    @Bridge(result=str)
    def getWindowId(self):
        """Returns the current window ID."""
        return self.window_id

    @Bridge()
    def closeWindow(self):
        """Closes the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.close_window()

    @Bridge()
    def hideWindow(self):
        """Hides the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.hide_window()

    @Bridge()
    def showWindow(self):
        """Shows and focuses the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.show_window()

    @Bridge()
    def toggleFullscreen(self):
        """Toggles fullscreen mode for the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.toggle_fullscreen()

    @Bridge()
    def minimizeWindow(self):
        """Minimizes the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.minimize_window()

    @Bridge()
    def maximizeWindow(self):
        """Maximizes the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.maximize_window()

    @Bridge()
    def restoreWindow(self):
        """Restores the window to its normal state."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.restore_window()

    @Bridge(str)
    def setUrl(self, url):
        """Sets the URL of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_url(url)


class BrowserWindow:
    def __init__(
        self,
        app,
        title,
        url,
        frame,
        context_menu,
        js_apis=[],
        enable_dev_tools=False,
        width=1200,
        height=800,
        x=100,
        y=100,
    ):
        self.id = str(uuid.uuid4())  # Generate unique ID
        self.app = app  # Store PylonApp instance
        self.js_apis = [WindowAPI(self.id, self.app)]

        self._window = QMainWindow()
        self._window.closeEvent = self.closeEvent  # Override closeEvent method
        self._window.setWindowTitle(title)
        self._window.setGeometry(x, y, width, height)

        self.web_view = QWebEngineView()
        self.title = title
        self.url = url
        self.frame = frame
        self.context_menu = context_menu
   
        self.enable_dev_tools = enable_dev_tools
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        # allow local file access to remote urls
        self.web_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        # Set icon
        self._window.setWindowIcon(self.app.icon)

        # Set Windows taskbar icon
        if sys.platform == "win32":
            import ctypes

            myappid = "mycompany.myproduct.subproduct.version"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Remove title bar and borders (if needed)
        if not frame:
            self._window.setWindowFlags(Qt.FramelessWindowHint)

        # Disable default context menu
        if not context_menu:
            self.web_view.setContextMenuPolicy(Qt.NoContextMenu)

        # Set up QWebChannel
        self.channel = QWebChannel()
        for js_api in js_apis:
            self.js_apis.append(js_api)

        # Register additional JS APIs
        if self.js_apis:
            for js_api in self.js_apis:
                self.channel.registerObject(js_api.__class__.__name__, js_api)

        self.web_view.page().setWebChannel(self.channel)

        # Load web page
        # Check if URL is a local HTML file
        if url.startswith("file://") or os.path.isfile(url) or url.endswith(".html"):
            self.load_html_file(url)
        else:
            self.web_view.setUrl(url)

        # Connect pylonjs bridge
        self.web_view.loadFinished.connect(self._on_load_finished)

        # Add QWebEngineView to main window
        self._window.setCentralWidget(self.web_view)

        # Set F12 shortcut
        if enable_dev_tools:
            self.dev_tools_shortcut = QShortcut(QKeySequence("F12"), self._window)
            self.dev_tools_shortcut.activated.connect(self.open_dev_window)

    def load_html_file(self, file_path):
        """Loads a local HTML file into the web view."""
        if file_path.startswith("file://"):
            file_path = file_path[7:]  # Remove 'file://'

        url = QUrl.fromLocalFile(file_path)

        self.web_view.setUrl(url)

    def _on_load_finished(self, ok):
        """Handles the event when the web page finishes loading."""
        if ok and self.js_apis:
            js_code = """
            if (typeof QWebChannel !== 'undefined') {
                new QWebChannel(qt.webChannelTransport, function (channel) {

                    window.pylon = {};

                    %s
                    // Dispatch a custom event to signal that the initialization is ready
                    const event = new CustomEvent('pylonReady');

                    document.dispatchEvent(event);
                });

            } else {

                console.error('QWebChannel is not defined.');

            }

            """
            js_api_init = "\n".join(
                [
                    f"window.pylon['{js_api.__class__.__name__}'] = channel.objects['{js_api.__class__.__name__}'];\n"
                    f"console.log('pylon.{js_api.__class__.__name__} object initialized:', window.pylon['{js_api.__class__.__name__}']);"
                    for js_api in self.js_apis
                ]
            )
            self.web_view.page().runJavaScript(js_code % js_api_init)
        else:
            pass

    def open_dev_window(self):
        """Opens the developer tools window."""
        self.web_view.page().setDevToolsPage(QWebEnginePage(self.web_view.page()))
        self.dev_tools_window = QMainWindow(self._window)
        dev_tools_view = QWebEngineView(self.dev_tools_window)
        dev_tools_view.setPage(self.web_view.page().devToolsPage())
        self.dev_tools_window.setCentralWidget(dev_tools_view)
        self.dev_tools_window.resize(800, 600)
        self.dev_tools_window.show()

    def get_window_properties(self):
        """Returns the properties of the window."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "frame": self.frame,
            "context_menu": self.context_menu,
            "enable_dev_tools": self.enable_dev_tools,
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
        }

    def closeEvent(self, event):
        """Handles the event when the window is closed."""
        self._remove_from_app_windows()
        event.accept()  # Accept the event (allow the window to close)

    def _remove_from_app_windows(self):
        """Removes the window from the app's window list."""
        if self in self.app.windows:
            self.app.windows.remove(self)
        if not self.app.windows:
            self.app.quit()  # Quit the app if all windows are closed

    def set_url(self, url):
        """Sets the URL of the window."""
        self.url = url
        if url.startswith("file://") or os.path.isfile(url) or url.endswith(".html"):
            self.load_html_file(url)
        else:
            self.web_view.setUrl(QUrl(url))

    ###########################################################################################
    # Window management (no ID required)
    ###########################################################################################
    def hide_window(self):
        """Hides the window."""
        self._window.hide()

    def show_window(self):
        """Shows and focuses the window."""
        self._window.show()
        self._window.activateWindow()
        self._window.raise_()
        self._window.setWindowState(self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)


    def close_window(self):
        """Closes the window."""
        self._window.close()

    def toggle_fullscreen(self):
        """Toggles fullscreen mode for the window."""
        if self._window.isFullScreen():
            self._window.showNormal()
        else:
            self._window.showFullScreen()

    def minimize_window(self):
        """Minimizes the window."""
        self._window.showMinimized()

    def maximize_window(self):
        """Maximizes the window."""
        self._window.showMaximized()

    def restore_window(self):
        """Restores the window to its normal state."""
        self._window.showNormal()


class _WindowController(QObject):
    hide_window_signal = Signal(str)
    show_window_signal = Signal(str)
    close_window_signal = Signal(str)
    stop_app_signal = Signal()
    create_window_signal = Signal(
        QApplication, str, str, bool, bool, list, bool, int, int, int, int
    )


class PylonApp(QApplication):
    def __init__(self, single_instance=True, icon_path=""):
        super().__init__(sys.argv)
        self.windows = []
        self.server = None

        self.single_instance = single_instance
        if self.single_instance:
            self._init_single_instance()

        self.controller = _WindowController()
        self.controller.create_window_signal.connect(self._create_window_function)
        # self.controller.hide_window_signal.connect(self._hide_window)
        # self.controller.show_window_signal.connect(self._show_window)
        # self.controller.close_window_signal.connect(self._close_window_by_id)
        # self.controller.stop_app_signal.connect(self.quit)

        self.tray_icon_path = None
        self.tray_icon = None
        self.tray_menu_items = []
        self.icon_path = icon_path
        self.icon = self.load_icon(icon_path)
        self.tray_icon_actions = {}  # Dictionary to store tray icon activation actions

    def load_icon(self, icon_path: str):
        """Loads an icon from the given path."""
        if is_production():
            icon_path = get_resource_path(icon_path)
        return QIcon(icon_path)

    def set_tray_icon_path(self, tray_icon_path: str):
        """Sets the path for the tray icon."""
        self.tray_icon_path = tray_icon_path
        self.tray_icon = self.load_icon(tray_icon_path)

    def set_tray_menu_items(self, tray_menu_items):
        """Sets the menu items for the tray icon."""
        self.tray_menu_items = tray_menu_items

    def create_window(
        self,
        url: str,
        title: str = "pylon",
        frame: bool = True,
        context_menu: bool = False,
        js_apis=[],
        enable_dev_tools=False,
        width=1200,
        height=800,
        x=300,
        y=300,
    ) -> BrowserWindow:
        """Creates a new browser window."""
        # Add 'file://' prefix if URL is a local file path ending with .html
        if os.path.isfile(url) or url.lower().endswith(".html"):
            url = f"file://{os.path.abspath(url)}"

        if is_production():
            url = f"file://{get_resource_path(url)}" # TODO : THINKING OTHER METHODS...

        self.controller.create_window_signal.emit(
            self,
            title,
            url,
            frame,
            context_menu,
            js_apis,
            enable_dev_tools,
            width,
            height,
            x,
            y,
        )
        return self.windows[-1]

    def _create_window_function(
        self,
        app,
        title: str,
        url: str,
        frame: bool,
        context_menu: bool,
        js_apis=[],
        enable_dev_tools=False,
        width=1200,
        height=800,
        x=100,
        y=100,
    ) -> BrowserWindow:
        """Function to create a new browser window."""
        window = BrowserWindow(
            app,
            title,
            url,
            frame,
            context_menu,
            js_apis,
            enable_dev_tools,
            width,
            height,
            x,
            y,
        )
        self.windows.append(window)
        window._window.show()
        if not self.windows:  # If it's the first window
            self.tray_icon.activated.connect(self.tray_icon_activated)
        return window

    def run(self):
        """Runs the application event loop."""
        sys.exit(self.exec())

    def _init_single_instance(self):
        """Initializes the application as a single instance."""
        socket = QLocalSocket()
        socket.connectToServer("PylonBrowserApp")
        if socket.waitForConnected(500):
            # Another instance is already running
            sys.exit(1)

        # Create a new server
        self.server = QLocalServer()
        self.server.listen("PylonBrowserApp")
        self.server.newConnection.connect(self._handle_new_connection)

    def _handle_new_connection(self):
        """Handles new connections for the single instance server."""
        pass

    
    ###########################################################################################
    # App windows
    ###########################################################################################
    def get_windows(self) -> List[BrowserWindow]:
        """Returns a list of all browser windows."""
        return self.windows

    def show_main_window(self):
        """Shows and focuses the first window."""
        if self.windows:
            main_window = self.windows[0]
            main_window._window.show()
            main_window._window.activateWindow()
            main_window._window.raise_()
            main_window._window.setWindowState(main_window._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

    ###########################################################################################
    # Window management in the app (ID required)
    ###########################################################################################

    def get_window_by_id(self, window_id: str) -> Optional[BrowserWindow]:
        """Returns the window with the given ID."""
        for window in self.windows:
            if window.id == window_id:
                return window
        return None

    def hide_window_by_id(self, window_id: str):
        """Hides the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window._window.hide()

    def show_window_by_id(self, window_id: str):
        """Shows and focuses the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window._window.show()
            window._window.activateWindow()
            window._window.raise_()
            window._window.setWindowState(window._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

    def close_window_by_id(self, window_id: str):
        """Closes the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window._window.close()

    def close_all_windows(self):
        """Closes all windows."""
        for window in self.windows:
            window._window.close()

    def quit(self):
        """Quits the application."""
        self.close_all_windows()
        QApplication.quit()

    def toggle_fullscreen_by_id(self, window_id: str):
        """Toggles fullscreen mode for the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            if window._window.isFullScreen():
                window._window.showNormal()
            else:
                window._window.showFullScreen()

    def minimize_window_by_id(self, window_id: str):
        """Minimizes the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window._window.showMinimized()

    def maximize_window_by_id(self, window_id: str):
        """Maximizes the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window._window.showMaximized()

    def restore_window_by_id(self, window_id: str):
        """Restores the window with the given ID to its normal state."""
        window = self.get_window_by_id(window_id)
        if window:
            window._window.showNormal()

    ###########################################################################################
    # Tray
    ###########################################################################################
    def setup_tray(self):
        """Sets up the system tray icon and menu."""
        self.tray = QSystemTrayIcon(self)
        if (
            self.tray_icon_path is None
        ):  # If tray icon is not set, use the default icon
            self.tray.setIcon(self.icon)
        else:
            self.tray.setIcon(self.tray_icon)

        tray_menu = QMenu()

        # Add menu items from external source
        if self.tray_menu_items:
            for item in self.tray_menu_items:
                action = tray_menu.addAction(item["label"])
                action.triggered.connect(item["callback"])

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()

    def tray_activated(self, reason):
        """Handles the event when the tray icon is activated."""
        reason_enum = QSystemTrayIcon.ActivationReason(reason)


        if reason_enum in self.tray_actions:
            self.tray_actions[reason_enum]()

    def set_tray_actions(self, actions):
        """
        Sets the actions for tray icon activation.

        actions: Dictionary where keys are TrayEvent enum values,
                 and values are callback functions for the respective activation reasons.
        """
        self.tray_actions = actions


if __name__ == "__main__":
    app = PylonApp(icon_path="assets/icon.ico")

    window = app.create_window(
        title="Pylon Browser",
        url="https://www.example.com",
        frame=True,
        context_menu=True,
        enable_dev_tools=True,
        width=1200,
        height=800,
        x=100,
        y=100,
    )

    window.show()

    app.run()