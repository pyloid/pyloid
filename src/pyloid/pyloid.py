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
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QClipboard, QImage
from PySide6.QtCore import Qt, Signal, QUrl, QObject
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from .api import PyloidAPI, Bridge
import uuid
from typing import List, Optional, Dict, Callable, Union, Any
from PySide6.QtCore import qInstallMessageHandler
import signal
from .utils import is_production
from .monitor import Monitor
import json
from .autostart import AutoStart

# for linux debug
os.environ['QTWEBENGINE_DICTIONARIES_PATH'] = '/'

# for macos debug

def custom_message_handler(mode, context, message):
    if not hasattr(custom_message_handler, 'vulkan_warning_shown') and (('Failed to load vulkan' in message) or ('No Vulkan library available' in message) or ('Failed to create platform Vulkan instance' in message)):
        print('\033[93mPyloid Warning: Vulkan GPU API issue detected. Switching to software backend.\033[0m')
        os.environ['QT_QUICK_BACKEND'] = 'software'
        custom_message_handler.vulkan_warning_shown = True
    if 'vulkan' not in message.lower():
        print(message)

qInstallMessageHandler(custom_message_handler)

class WindowAPI(PyloidAPI):
    def __init__(self, window_id: str, app):
        super().__init__()
        self.window_id: str = window_id
        self.app: Pyloid = app

    @Bridge(result=str)
    def getWindowId(self):
        """Returns the current window ID."""
        return self.window_id

    @Bridge()
    def close(self):
        """Closes the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.close()

    @Bridge()
    def hide(self):
        """Hides the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.hide()

    @Bridge()
    def show(self):
        """Shows and focuses the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.show()

    @Bridge()
    def toggleFullscreen(self):
        """Toggles fullscreen mode for the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.toggle_fullscreen()

    @Bridge()
    def minimize(self):
        """Minimizes the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.minimize()

    @Bridge()
    def maximize(self):
        """Maximizes the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.maximize()

    @Bridge()
    def unmaximize(self):
        """Restores the window to its normal state."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.unmaximize()

    @Bridge(str)
    def setTitle(self, title: str):
        """Sets the title of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_title(title)

    @Bridge(int, int)
    def setSize(self, width: int, height: int):
        """Sets the size of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_size(width, height)

    @Bridge(int, int)
    def setPosition(self, x: int, y: int):
        """Sets the position of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_position(x, y)

    @Bridge(bool)
    def setFrame(self, frame: bool):
        """Sets the frame of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_frame(frame)

    @Bridge(bool)
    def setContextMenu(self, context_menu: bool):
        """Sets the context menu of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_context_menu(context_menu)

    @Bridge(bool)
    def setDevTools(self, enable: bool):
        """Sets the developer tools of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.set_dev_tools(enable)

    @Bridge(str, result=Optional[str])
    def capture(self, save_path: str) -> Optional[str]:
        """Captures the current window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            return window.capture(save_path)
        return None

# class EventAPI(PylonAPI):
#     def __init__(self, window_id: str, app):
#         super().__init__()
#         self.window_id: str = window_id
#         self.app: PylonApp = app
#         self.subscribers = {}

#     @Bridge(str, Callable)
#     def on(self, event_name: str, callback: Callable):
#         """특정 이벤트를 구독합니다."""
#         if event_name not in self.subscribers:
#             self.subscribers[event_name] = []
#         self.subscribers[event_name].append(callback)

#     @Bridge(str, result=Optional[str])
#     def emit(self, event_name: str, *args, **kwargs):
#         """다른 윈도우로 특정 이벤트를 보냅니다."""
#         if event_name in self.subscribers:
#             for callback in self.subscribers[event_name]:
#                 callback(*args, **kwargs)

        

class BrowserWindow:
    def __init__(
        self,
        app,
        title: str="pyloid app",
        width: int=800,
        height: int=600,
        x: int=200,
        y: int=200,
        frame: bool=True,
        context_menu: bool=False,
        dev_tools: bool=False,
        js_apis: List[PyloidAPI]=[],
    ):
        ###########################################################################################
        self.id = str(uuid.uuid4())  # Generate unique ID

        self._window = QMainWindow()
        self.web_view = QWebEngineView()

        self._window.closeEvent = self.closeEvent  # Override closeEvent method 
        ###########################################################################################
        self.app = app 
        self.title = title
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.frame = frame
        self.context_menu = context_menu
        self.dev_tools = dev_tools
        self.js_apis = [WindowAPI(self.id, self.app)]
        for js_api in js_apis:
            self.js_apis.append(js_api)
        self.shortcuts = {}
        ###########################################################################################
    
    def _load(self):
        self._window.setWindowTitle(self.title)

        self._window.setGeometry(self.x, self.y, self.width, self.height)

        # allow local file access to remote urls
        self.web_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        # Set icon
        if self.app.icon:
            self._window.setWindowIcon(self.app.icon)
        else:
            print("Icon is not set.")

        # Set Windows taskbar icon
        if sys.platform == "win32":
            import ctypes

            myappid = "mycompany.myproduct.subproduct.version"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        
        # Remove title bar and borders (if needed)
        if not self.frame:
            self._window.setWindowFlags(Qt.FramelessWindowHint)

        # Disable default context menu
        if not self.context_menu:
            self.web_view.setContextMenuPolicy(Qt.NoContextMenu)

        # Set up QWebChannel
        self.channel = QWebChannel()

        # Register additional JS APIs
        if self.js_apis:
            for js_api in self.js_apis:
                self.channel.registerObject(js_api.__class__.__name__, js_api)
        

        self.web_view.page().setWebChannel(self.channel)

        # Connect pylonjs bridge
        self.web_view.loadFinished.connect(self._on_load_finished)

        # Add QWebEngineView to main window
        self._window.setCentralWidget(self.web_view)
        

        # Set F12 shortcut
        self.set_dev_tools(self.dev_tools)

    def _on_load_finished(self, ok):
        """Handles the event when the web page finishes loading."""
        if ok and self.js_apis:
            js_code = """
            if (typeof QWebChannel !== 'undefined') {
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    window.pyloid = {
                        EventAPI: {
                            listen: function(eventName, callback) {
                                document.addEventListener(eventName, function(event) {
                                    let eventData;
                                    try {
                                        eventData = JSON.parse(event.detail);
                                    } catch (e) {
                                        eventData = event.detail;
                                    }
                                    callback(eventData);
                                });
                            },
                            unlisten: function(eventName) {
                                document.removeEventListener(eventName);
                            }
                        }   
                    };
                    console.log('pyloid.EventAPI object initialized:', window.pyloid.EventAPI);

                    %s

                    // Dispatch a custom event to signal that the initialization is ready
                    const event = new CustomEvent('pyloidReady');
                    document.dispatchEvent(event);
                });
            } else {
                console.error('QWebChannel is not defined.');
            }
            """
            js_api_init = "\n".join(
                [
                    f"window.pyloid['{js_api.__class__.__name__}'] = channel.objects['{js_api.__class__.__name__}'];\n"
                    f"console.log('pyloid.{js_api.__class__.__name__} object initialized:', window.pyloid['{js_api.__class__.__name__}']);"
                    for js_api in self.js_apis
                ]
            )
            self.web_view.page().runJavaScript(js_code % js_api_init)
        else:
            pass

    ###########################################################################################
    # Load
    ###########################################################################################
    def load_file(self, file_path):
        """Loads a local HTML file into the web view."""
        self._load()
        file_path = os.path.abspath(file_path) # absolute path
        self.web_view.setUrl(QUrl.fromLocalFile(file_path))
        

    def load_url(self, url):
        """Sets the URL of the window."""
        self._load()
        self.web_view.setUrl(QUrl(url))
    ###########################################################################################
    # Set Parameters
    ###########################################################################################
    def set_title(self, title: str):
        """Sets the title of the window."""
        self.title = title
        self._window.setWindowTitle(self.title)

    def set_size(self, width: int, height: int):
        """Sets the size of the window."""
        self.width = width
        self.height = height
        self._window.setGeometry(self.x, self.y, self.width, self.height)

    def set_position(self, x: int, y: int):
        """Sets the position of the window."""
        self.x = x
        self.y = y
        self._window.setGeometry(self.x, self.y, self.width, self.height)

    def set_frame(self, frame: bool):
        """Sets the frame of the window."""
        self.frame = frame
        if self.frame:
            self._window.setWindowFlags(Qt.Window)
        else:
            self._window.setWindowFlags(Qt.FramelessWindowHint)

    def set_context_menu(self, context_menu: bool):
        """Sets the context menu of the window."""
        self.context_menu = context_menu
        if self.context_menu:
            self.web_view.setContextMenuPolicy(Qt.NoContextMenu)
        else:
            self.web_view.setContextMenuPolicy(Qt.DefaultContextMenu)
        
    def set_dev_tools(self, enable: bool):
        """Sets the developer tools of the window.
        
        If enabled, the developer tools can be opened using the F12 key.
        """
        self.dev_tools = enable
        if self.dev_tools:
            self.add_shortcut("F12", self.open_dev_tools)
        else:
            self.remove_shortcut("F12")

    def open_dev_tools(self):
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
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
            "frame": self.frame,
            "context_menu": self.context_menu,
            "dev_tools": self.dev_tools,
            "js_apis": self.js_apis,
        }
    
    def get_id(self):
        """Returns the ID of the window."""
        return self.id

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

    ###########################################################################################
    # Window management (no ID required)
    ###########################################################################################
    def hide(self):
        """Hides the window."""
        self._window.hide()

    def show(self):
        """Shows the window."""
        self._window.show()
    
    def focus(self):
        """Focuses the window."""
        self._window.activateWindow()
        self._window.raise_()
        self._window.setWindowState(self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

    def show_and_focus(self):
        """Shows and focuses the window."""
        self._window.show()
        self._window.activateWindow()
        self._window.raise_()
        self._window.setWindowState(self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

    def close(self):
        """Closes the window."""
        self._window.close()

    def toggle_fullscreen(self):
        """Toggles fullscreen mode for the window."""
        if self._window.isFullScreen():
            self._window.showNormal()
        else:
            self._window.showFullScreen()

    def minimize(self):
        """Minimizes the window."""
        self._window.showMinimized()

    def maximize(self):
        """Maximizes the window."""
        self._window.showMaximized()

    def unmaximize(self):
        """Unmaximizes the window."""
        self._window.showNormal()

    def capture(self, save_path: str) -> Optional[str]:
        """
        Captures the current window.
        
        :param save_path: Path to save the captured image. If not specified, it will be saved in the current directory.
        :return: Path of the saved image
        """
        try:
            # Capture window
            screenshot = self._window.grab()
            
            # Save image
            screenshot.save(save_path)
            return save_path
        except Exception as e:
            print(f"Error occurred while capturing the window: {e}")
            return None

    ###########################################################################################
    # Shortcut
    ###########################################################################################
    def add_shortcut(self, key_sequence: str, callback: Callable):
        """
        Adds a keyboard shortcut to the window if it does not already exist.
        
        :param key_sequence: Shortcut sequence (e.g., "Ctrl+C")
        :param callback: Function to be executed when the shortcut is pressed
        :return: Created QShortcut object or None if the shortcut already exists
        """
        if key_sequence in self.shortcuts:
            # print(f"Shortcut {key_sequence} already exists.")
            return None
        
        shortcut = QShortcut(QKeySequence(key_sequence), self._window)
        shortcut.activated.connect(callback)
        self.shortcuts[key_sequence] = shortcut
        return shortcut

    def remove_shortcut(self, key_sequence: str):
        """
        Removes a keyboard shortcut from the window.
        
        :param key_sequence: Shortcut sequence to be removed
        """
        if key_sequence in self.shortcuts:
            shortcut = self.shortcuts.pop(key_sequence)
            shortcut.setEnabled(False)
            shortcut.deleteLater()

    def get_all_shortcuts(self):
        """
        Returns all registered shortcuts in the window.
        
        :return: Dictionary of shortcut sequences and QShortcut objects
        """
        return self.shortcuts
    
    ###########################################################################################
    # Event (Calling the JS from Python)
    ###########################################################################################
    def emit(self, event_name, data: Optional[Dict]=None):
        """
        Emits an event to the JavaScript side.
        
        :param event_name: Name of the event
        :param data: Data to be sent with the event (optional)
        """
        script = f"""
        (function() {{
            const eventData = {json.dumps(data)};
            const customEvent = new CustomEvent('{event_name}', {{ detail: eventData }});
            document.dispatchEvent(customEvent);
        }})();
        """
        self.web_view.page().runJavaScript(script)


class _WindowController(QObject):
    create_window_signal = Signal(
        QApplication, str, int, int, int, int, bool, bool, bool, list
    )

class Pyloid(QApplication):
    def __init__(self, app_name, single_instance=True, icon_path: str=None, tray_icon_path: str=None):
        super().__init__(sys.argv)

        self.windows = []
        self.server = None

        self.clipboard_class = self.clipboard()
        self.shortcuts = {}

        self.single_instance = single_instance
        if self.single_instance:
            self._init_single_instance()

        self.controller = _WindowController()
        self.controller.create_window_signal.connect(self._create_window_signal_function)

        self.icon = QIcon(icon_path) if icon_path else None
        self.tray_icon = QIcon(tray_icon_path) if tray_icon_path else None
        self.tray_menu_items = []
        self.tray_actions = {}

        self.app_name = app_name
        self.app_path = sys.executable

        self.auto_start = AutoStart(self.app_name, self.app_path)

    def set_icon(self, icon_path: str):
        """Sets the icon for the application."""
        self.icon = QIcon(icon_path)

    def set_tray_icon(self, tray_icon_path: str):
        """Sets the path for the tray icon."""
        self.tray_icon = QIcon(tray_icon_path)

    def set_tray_menu_items(self, tray_menu_items: Dict[str, Callable]):
        """Sets the menu items for the tray icon."""
        self.tray_menu_items = tray_menu_items

    def create_window(
        self,
        title: str="pyloid app",
        width: int=800,
        height: int=600,
        x: int=200,
        y: int=200,
        frame: bool=True,
        context_menu: bool=False,
        dev_tools: bool=False,
        js_apis: List[PyloidAPI]=[],
    ) -> BrowserWindow:
        """Creates a new browser window."""
        self.controller.create_window_signal.emit(
            self,
            title,
            width,
            height,
            x,
            y,
            frame,
            context_menu,
            dev_tools,
            js_apis,
        )
        return self.windows[-1]

    def _create_window_signal_function(
        self,
        app,
        title: str,
        width: int,
        height: int,
        x: int,
        y: int,
        frame: bool,
        context_menu: bool,
        dev_tools: bool,
        js_apis: List[PyloidAPI]=[],
    ) -> BrowserWindow:
        """Function to create a new browser window."""
        window = BrowserWindow(
            app,
            title,
            width,
            height,
            x,
            y,
            frame,
            context_menu,
            dev_tools,
            js_apis,
        )
        self.windows.append(window)
        return window

    def run(self):
        """Runs the application event loop."""
        if is_production():
            sys.exit(self.exec())
        else:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            sys.exit(self.exec())

    def _init_single_instance(self):
        """Initializes the application as a single instance."""
        socket = QLocalSocket()
        socket.connectToServer("PyloidBrowserApp")
        if socket.waitForConnected(500):
            # Another instance is already running
            sys.exit(1)

        # Create a new server
        self.server = QLocalServer()
        self.server.listen("PyloidBrowserApp")
        self.server.newConnection.connect(self._handle_new_connection)

    def _handle_new_connection(self):
        """Handles new connections for the single instance server."""
        pass

    
    ###########################################################################################
    # App window
    ###########################################################################################
    def get_windows(self) -> List[BrowserWindow]:
        """Returns a list of all browser windows."""
        return self.windows

    def show_main_window(self):
        """Shows and focuses the first window."""
        if self.windows:
            main_window = self.windows[0]
            main_window._window.show()

    def focus_main_window(self):
        """Focuses the first window."""
        if self.windows:
            main_window = self.windows[0]
            main_window._window.activateWindow()
            main_window._window.raise_()
            main_window._window.setWindowState(main_window._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    
    def show_and_focus_main_window(self):
        """Shows and focuses the first window."""
        if self.windows:
            main_window = self.windows[0]
            main_window._window.show()
            main_window._window.activateWindow()
            main_window._window.raise_()
            main_window._window.setWindowState(main_window._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    
    def close_all_windows(self):
        """Closes all windows."""
        for window in self.windows:
            window._window.close()

    def quit(self):
        """Quits the application."""
        self.close_all_windows()
        QApplication.quit()
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
            window.hide()

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

    def toggle_fullscreen_by_id(self, window_id: str):
        """Toggles fullscreen mode for the window with the given ID."""
        window = self.get_window_by_id(window_id)
        window.toggle_fullscreen()

    def minimize_window_by_id(self, window_id: str):
        """Minimizes the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window.minimize()

    def maximize_window_by_id(self, window_id: str):
        """Maximizes the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window.maximize()

    def unmaximize_window_by_id(self, window_id: str):
        """Unmaximizes the window with the given ID."""
        window = self.get_window_by_id(window_id)
        if window:
            window.unmaximize()

    def capture_window_by_id(self, window_id: str, save_path: str) -> Optional[str]:
        """
        Captures a specific window.
        
        :param window_id: ID of the window to capture
        :param save_path: Path to save the captured image. If not specified, it will be saved in the current directory.
        :return: Path of the saved image
        """
        try:
            window = self.get_window_by_id(window_id)
            if not window:
                print(f"Cannot find window with the specified ID: {window_id}")
                return None
            
            # Capture window
            screenshot = window._window.grab()
            
            # Save image
            screenshot.save(save_path)
            return save_path
        except Exception as e:
            print(f"Error occurred while capturing the window: {e}")
            return None
    ###########################################################################################
    # Tray
    ###########################################################################################
    def run_tray(self):
        """Sets up the system tray icon and menu."""
        if not hasattr(self, 'tray'):
            self.tray = QSystemTrayIcon(self)
            if self.tray_icon:
                self.tray.setIcon(self.tray_icon)
            else:
                if self.icon:
                    self.tray.setIcon(self.icon)
                else:
                    print("Icon and Tray icon are not set.")

            tray_menu = QMenu()

            # Add menu items from external source
            if self.tray_menu_items:
                for item in self.tray_menu_items:
                    action = tray_menu.addAction(item["label"])
                    action.triggered.connect(item["callback"])

            self.tray.setContextMenu(tray_menu)
            self.tray.activated.connect(self._tray_activated)
            self.tray.show()

    def _tray_activated(self, reason):
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

    def show_notification(self, title: str, message: str):
        """Displays a notification in the system tray."""
        if not hasattr(self, 'tray'):
            self.run_tray()  # Ensure the tray is initialized

        self.tray.showMessage(title, message, QIcon(self.icon), 5000)

    ###########################################################################################
    # Monitor
    ###########################################################################################
    def get_all_monitors(self) -> List[Monitor]:
        """
        Returns a list of information for all connected monitors.
        
        :return: List containing monitor information
        """
        monitors = [Monitor(index, screen) for index, screen in enumerate(self.screens())]
        return monitors
    
    def get_primary_monitor(self) -> Monitor:
        """
        Returns information for the primary monitor.
        
        :return: Primary monitor information
        """
        primary_monitor = self.screens()[0]
        return Monitor(0, primary_monitor)
    
    ###########################################################################################
    # Clipboard
    ###########################################################################################
    def copy_to_clipboard(self, text):
        """
        Copies text to the clipboard.
        
        :param text: Text to be copied
        """
        self.clipboard_class.setText(text, QClipboard.Clipboard)

    def get_clipboard_text(self):
        """
        Retrieves text from the clipboard.
        
        :return: Text from the clipboard
        """
        return self.clipboard_class.text()

    def set_clipboard_image(self, image: Union[str, bytes, os.PathLike]):
        """
        Copies an image to the clipboard.
        
        :param image: Path to the image to be copied
        """
        self.clipboard_class.setImage(QImage(image), QClipboard.Clipboard)

    def get_clipboard_image(self):
        """
        Retrieves an image from the clipboard.
        
        :return: QImage object from the clipboard (None if no image)
        """
        return self.clipboard_class.image()
    
    ###########################################################################################
    # Atostart
    ###########################################################################################
    def set_auto_start(self, enable: bool):
        """
        Sets the application to start automatically with the system. (set_auto_start(True) only works in production)
        True only works in production.
        False works in both environments.
        
        :param enable: True to enable auto-start, False to disable
        """
        if not enable:
            self.auto_start.set_auto_start(False)
            return False

        if is_production():
            if enable:
                self.auto_start.set_auto_start(True)
                return True
        else:
            print("\033[93mset_auto_start(True) is not supported in non-production environment\033[0m")
            return None

    def is_auto_start(self):
        """
        Checks if the application is set to start automatically with the system.

        :return: True if auto-start is enabled, False otherwise
        """
        
        return self.auto_start.is_auto_start()
        

