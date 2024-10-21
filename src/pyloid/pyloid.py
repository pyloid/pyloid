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
from PySide6.QtGui import (
    QIcon,
    QKeySequence,
    QShortcut,
    QClipboard,
    QImage,
    QAction,
    QCursor,
)
from PySide6.QtCore import Qt, Signal, QPoint, QUrl, QObject, QTimer, QSize, QEvent
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
from .filewatcher import FileWatcher
import logging
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from .custom.titlebar import CustomTitleBar

# for linux debug
os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = "/"

# for macos debug
logging.getLogger("Qt").setLevel(logging.ERROR)


def custom_message_handler(mode, context, message):
    if not hasattr(custom_message_handler, "vulkan_warning_shown") and (
        ("Failed to load vulkan" in message)
        or ("No Vulkan library available" in message)
        or ("Failed to create platform Vulkan instance" in message)
    ):
        print(
            "\033[93mPyloid Warning: Vulkan GPU API issue detected. Switching to software backend.\033[0m"
        )
        os.environ["QT_QUICK_BACKEND"] = "software"
        custom_message_handler.vulkan_warning_shown = True

    if "Autofill.enable failed" in message:
        print(
            "\033[93mPyloid Warning: Autofill is not enabled in developer tools.\033[0m"
        )

    if "vulkan" not in message.lower() and "Autofill.enable failed" not in message:
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

    @Bridge(result=dict)
    def getWindowProperties(self):
        """Returns the properties of the window."""
        window = self.app.get_window_by_id(self.window_id)
        window_properties = window.get_window_properties()
        return window_properties

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

    @Bridge(result=bool)
    def getFrame(self):
        """Returns whether the window has a frame."""
        window = self.app.get_window_by_id(self.window_id)
        return window.frame if window else False

    @Bridge(result=bool)
    def getContextMenu(self):
        """Returns whether the window has a context menu."""
        window = self.app.get_window_by_id(self.window_id)
        return window.context_menu if window else False

    @Bridge(result=bool)
    def getDevTools(self):
        """Returns whether the window has developer tools."""
        window = self.app.get_window_by_id(self.window_id)
        return window.dev_tools if window else False

    @Bridge(result=str)
    def getTitle(self):
        """Returns the title of the window."""
        window = self.app.get_window_by_id(self.window_id)
        return window.title if window else ""

    @Bridge(result=dict)
    def getSize(self):
        """Returns the size of the window."""
        window = self.app.get_window_by_id(self.window_id)
        return (
            {"width": window.width, "height": window.height}
            if window
            else {"width": 0, "height": 0}
        )

    @Bridge(result=dict)
    def getPosition(self):
        """Returns the position of the window."""
        window = self.app.get_window_by_id(self.window_id)
        return {"x": window.x, "y": window.y} if window else {"x": 0, "y": 0}

    @Bridge()
    def startSystemDrag(self):
        """Starts the system drag."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.web_view.start_system_drag()


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


# 어차피 load 부분에만 쓰이니까 나중에 분리해서 load 위에서 선언하자.
class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent._window)
        self.parent = parent
        self.drag_relative_position = None
        self.is_dragging = False
        self.is_resizing = False
        self.resize_start_pos = None
        self.resize_direction = None
        self.screen_geometry = self.screen().availableGeometry()
        self.is_resizing_enabled = True

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_relative_position = event.pos()
            if not self.parent.frame and self.is_resizing_enabled:
                self.resize_direction = self.get_resize_direction(event.pos())
                if self.resize_direction:
                    self.is_resizing = True
                    self.resize_start_pos = event.globalPos()

    def start_system_drag(self):
        self.is_dragging = True

    def mouse_move_event(self, event):
        if self.is_resizing and self.is_resizing_enabled:
            self.resize_window(event.globalPos())
        elif not self.parent.frame and self.is_dragging:
            # 현재 마우스 위치를 전역 좌표로 가져옵니다
            current_global_pos = event.globalPos()

            # 화면 경계를 계산합니다
            left_boundary = self.screen_geometry.left()
            right_boundary = self.screen_geometry.right()
            top_boundary = self.screen_geometry.top()
            bottom_boundary = self.screen_geometry.bottom()

            # 마우스 커서 위치를 제한합니다
            new_cursor_pos = QPoint(
                max(left_boundary, min(current_global_pos.x(), right_boundary)),
                max(top_boundary, min(current_global_pos.y(), bottom_boundary)),
            )

            # 마우스 커서를 새 위치로 이동합니다
            QCursor.setPos(new_cursor_pos)

            # 창의 새 위치를 계산합니다
            new_window_pos = new_cursor_pos - self.drag_relative_position

            # 창을 새 위치로 이동합니다
            self.parent._window.move(new_window_pos)
        else:
            # Change cursor based on resize direction
            resize_direction = self.get_resize_direction(event.pos())
            if resize_direction and self.is_resizing_enabled:
                self.set_cursor_for_resize_direction(resize_direction)
            else:
                self.unsetCursor()

    def mouse_release_event(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.is_resizing = False
            self.resize_direction = None
            self.unsetCursor()

    def eventFilter(self, source, event):
        if self.focusProxy() is source:
            if event.type() == QEvent.MouseButtonPress:
                self.mouse_press_event(event)
            elif event.type() == QEvent.MouseMove:
                self.mouse_move_event(event)
            elif event.type() == QEvent.MouseButtonRelease:
                self.mouse_release_event(event)
        return super().eventFilter(source, event)

    def get_resize_direction(self, pos):
        if not self.parent.frame and self.is_resizing_enabled:  # Check if frame is not present and resizing is enabled
            margin = 5  # Margin in pixels to detect edge
            rect = self.rect()
            direction = None

            if pos.x() <= margin:
                direction = 'left'
            elif pos.x() >= rect.width() - margin:
                direction = 'right'

            if pos.y() <= margin:
                direction = 'top' if direction is None else direction + '-top'
            elif pos.y() >= rect.height() - margin:
                direction = 'bottom' if direction is None else direction + '-bottom'

            return direction
        return None

    def set_cursor_for_resize_direction(self, direction):
        if not self.parent.frame and direction and self.is_resizing_enabled:  # Check if frame is not present and resizing is enabled
            if direction in ['left', 'right']:
                self.setCursor(Qt.SizeHorCursor)
            elif direction in ['top', 'bottom']:
                self.setCursor(Qt.SizeVerCursor)
            elif direction in ['left-top', 'right-bottom']:
                self.setCursor(Qt.SizeFDiagCursor)
            elif direction in ['right-top', 'left-bottom']:
                self.setCursor(Qt.SizeBDiagCursor)

    def resize_window(self, global_pos):
        if not self.parent.frame and self.resize_start_pos and self.resize_direction and self.is_resizing_enabled:  # Check if frame is not present and resizing is enabled
            delta = global_pos - self.resize_start_pos
            new_geometry = self.parent._window.geometry()

            if 'left' in self.resize_direction:
                new_geometry.setLeft(new_geometry.left() + delta.x())
            if 'right' in self.resize_direction:
                new_geometry.setRight(new_geometry.right() + delta.x())
            if 'top' in self.resize_direction:
                new_geometry.setTop(new_geometry.top() + delta.y())
            if 'bottom' in self.resize_direction:
                new_geometry.setBottom(new_geometry.bottom() + delta.y())

            self.parent._window.setGeometry(new_geometry)
            self.resize_start_pos = global_pos


class BrowserWindow:
    def __init__(
        self,
        app,
        title: str = "pyloid app",
        width: int = 800,
        height: int = 600,
        x: int = 200,
        y: int = 200,
        frame: bool = True,
        context_menu: bool = False,
        dev_tools: bool = False,
        js_apis: List[PyloidAPI] = [],
    ):
        ###########################################################################################
        self.id = str(uuid.uuid4())  # Generate unique ID
        self._window = QMainWindow()
        self.web_view = CustomWebEngineView(self)

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

    def _set_custom_frame(
        self,
        use_custom: bool,
        title: str = "Custom Title",
        bg_color: str = "darkblue",
        text_color: str = "white",
        icon_path: str = None,
    ):
        """Sets or removes the custom frame."""
        if use_custom:
            self._window.setWindowFlags(Qt.FramelessWindowHint)
            self.custom_title_bar = CustomTitleBar(self._window)
            self.custom_title_bar.set_style(bg_color, text_color)
            self.custom_title_bar.set_title(title)

            if icon_path:
                self.custom_title_bar.set_icon(icon_path)

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.custom_title_bar)
            layout.addWidget(self.web_view)

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self._window.setCentralWidget(central_widget)

            # Add properties for window movement
            self._window.moving = False
            self._window.offset = QPoint()
        else:
            self._window.setWindowFlags(Qt.Window)
            self._window.setCentralWidget(self.web_view)
            self.custom_title_bar = None

        self._window.show()

    def _load(self):
        self.set_title(self.title)

        self.set_size(self.width, self.height)
        self.set_position(self.x, self.y)

        # allow local file access to remote urls
        self.web_view.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
        )

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
                    
                    document.addEventListener('mousedown', function (e) {
                        if (e.target.hasAttribute('data-pyloid-drag-region')) {
                            window.pyloid.WindowAPI.startSystemDrag();
                        }
                    });

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
        file_path = os.path.abspath(file_path)  # absolute path
        self.web_view.setUrl(QUrl.fromLocalFile(file_path))
        self.web_view.focusProxy().installEventFilter(self.web_view)

    def load_url(self, url):
        """Sets the URL of the window."""
        self._load()
        self.web_view.setUrl(QUrl(url))
        self.web_view.focusProxy().installEventFilter(self.web_view)

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
        was_visible = self._window.isVisible()
        if self.frame:
            self._window.setWindowFlags(Qt.Window)
        else:
            self._window.setWindowFlags(Qt.FramelessWindowHint)
        if was_visible:
            self._window.show()

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

        # Add this line to handle dev tools window closure
        self.dev_tools_window.closeEvent = lambda event: setattr(
            self, "dev_tools_window", None
        )

    def closeEvent(self, event):
        """Handles the event when the window is closed."""
        # Close developer tools if open
        if hasattr(self, "dev_tools_window") and self.dev_tools_window:
            self.dev_tools_window.close()
            self.dev_tools_window = None

        # Solve memory leak issue with web view engine
        self.web_view.page().deleteLater()
        self.web_view.deleteLater()
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
        self._window.setWindowState(
            self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )

    def show_and_focus(self):
        """Shows and focuses the window."""
        self._window.show()
        self._window.activateWindow()
        self._window.raise_()
        self._window.setWindowState(
            self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )

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
    def emit(self, event_name, data: Optional[Dict] = None):
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

    ###########################################################################################
    # Get Properties
    ###########################################################################################
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
        }

    def get_id(self):
        """Returns the ID of the window."""
        return self.id

    def get_size(self) -> Dict[str, int]:
        """Returns the size of the window."""
        return {"width": self.width, "height": self.height}

    def get_position(self) -> Dict[str, int]:
        """Returns the position of the window."""
        return {"x": self.x, "y": self.y}

    def get_title(self) -> str:
        """Returns the title of the window."""
        return self.title

    def get_url(self) -> str:
        """Returns the URL of the window."""
        return self.web_view.url().toString()

    def get_visible(self) -> bool:
        """Returns the visibility of the window."""
        return self._window.isVisible()
    
    def get_frame(self) -> bool:
        """Returns the frame enabled state of the window."""
        return self.frame
    
    ###########################################################################################
    # Resize
    ###########################################################################################
    def set_resizable(self, resizable: bool):
        """Sets the resizability of the window."""
        self.resizable = resizable
        if self.frame:
            flags = self._window.windowFlags() | Qt.WindowCloseButtonHint
            if resizable:
                pass
            else:
                flags |= Qt.MSWindowsFixedSizeDialogHint
            self._window.setWindowFlags(flags)
        else:
            # 프레임이 없는 경우 커스텀 리사이징 로직을 설정합니다.
            self.web_view.is_resizing_enabled = resizable

        self._window.show()  # 변경사항을 적용하기 위해 창을 다시 표시합니다.

    def set_minimum_size(self, min_width: int, min_height: int):
        """Sets the minimum size of the window."""
        self._window.setMinimumSize(min_width, min_height)

    def set_maximum_size(self, max_width: int, max_height: int):
        """Sets the maximum size of the window."""
        self._window.setMaximumSize(max_width, max_height)

    def get_minimum_size(self):
        """Returns the minimum size of the window."""
        return {'width': self._window.minimumWidth(), 'height': self._window.minimumHeight()}

    def get_maximum_size(self):
        """Returns the maximum size of the window."""
        return {'width': self._window.maximumWidth(), 'height': self._window.maximumHeight()}
    
    def get_resizable(self):
        """Returns the resizability of the window."""
        return self.resizable

class _WindowController(QObject):
    create_window_signal = Signal(
        QApplication, str, int, int, int, int, bool, bool, bool, list
    )


class Pyloid(QApplication):
    def __init__(
        self,
        app_name,
        single_instance=True,
    ):
        super().__init__(sys.argv)

        self.windows = []
        self.server = None

        self.app_name = app_name
        self.icon = None

        self.clipboard_class = self.clipboard()
        self.shortcuts = {}

        self.single_instance = single_instance
        if self.single_instance:
            self._init_single_instance()

        self.controller = _WindowController()
        self.controller.create_window_signal.connect(
            self._create_window_signal_function
        )

        self.file_watcher = FileWatcher()

        self.tray_menu_items = []
        self.tray_actions = {}

        self.app_name = app_name
        self.app_path = sys.executable

        self.auto_start = AutoStart(self.app_name, self.app_path)

        self.animation_timer = None
        self.icon_frames = []
        self.current_frame = 0

    def set_icon(self, icon_path: str):
        """
        Dynamically sets the application's icon.

        :param icon_path: Path to the new icon file

        This method can be called while the application is running.
        The icon can be changed at any time and is applied immediately.
        """
        self.icon = QIcon(icon_path)

        # Immediately update the icon for all open windows
        for window in self.windows:
            window._window.setWindowIcon(self.icon)

    def create_window(
        self,
        title: str = "pyloid app",
        width: int = 800,
        height: int = 600,
        x: int = 200,
        y: int = 200,
        frame: bool = True,
        context_menu: bool = False,
        dev_tools: bool = False,
        js_apis: List[PyloidAPI] = [],
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
        js_apis: List[PyloidAPI] = [],
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
        socket.connectToServer(self.app_name)
        if socket.waitForConnected(500):
            # Another instance is already running
            sys.exit(1)

        # Create a new server
        self.server = QLocalServer()
        self.server.listen(self.app_name)
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
            main_window._window.setWindowState(
                main_window._window.windowState() & ~Qt.WindowMinimized
                | Qt.WindowActive
            )

    def show_and_focus_main_window(self):
        """Shows and focuses the first window."""
        if self.windows:
            main_window = self.windows[0]
            main_window._window.show()
            main_window._window.activateWindow()
            main_window._window.raise_()
            main_window._window.setWindowState(
                main_window._window.windowState() & ~Qt.WindowMinimized
                | Qt.WindowActive
            )

    def close_all_windows(self):
        """Closes all windows."""
        for window in self.windows:
            window._window.close()

    def quit(self):
        """애플리케이션을 종료합니다."""
        for window in self.windows:
            window._window.close()
            window.web_page.deleteLater()
            window.web_view.deleteLater()
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
            window._window.setWindowState(
                window._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
            )

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
    def set_tray_icon(self, tray_icon_path: str):
        """
        Dynamically sets the tray icon.
        Can be called while the application is running, and changes are applied immediately.

        :param tray_icon_path: Path to the new tray icon file
        """
        # Stop and remove existing animation timer if present
        if hasattr(self, "animation_timer") and self.animation_timer is not None:
            self.animation_timer.stop()
            self.animation_timer.deleteLater()
            self.animation_timer = None

        # Remove existing icon frames
        if hasattr(self, "icon_frames"):
            self.icon_frames = []

        # Set new icon
        self.tray_icon = QIcon(tray_icon_path)

        if not hasattr(self, "tray"):
            self._init_tray()
        else:
            self.tray.setIcon(self.tray_icon)

    def set_tray_menu_items(
        self, tray_menu_items: List[Dict[str, Union[str, Callable]]]
    ):
        """
        Dynamically sets the tray menu items.
        Can be called while the application is running, and changes are applied immediately.

        :param tray_menu_items: List of new tray menu items
        """
        self.tray_menu_items = tray_menu_items
        if not hasattr(self, "tray"):
            self._init_tray()
        self._update_tray_menu()

    def _init_tray(self):
        """Initializes the tray icon."""
        self.tray = QSystemTrayIcon(self)
        if self.tray_icon:
            self.tray.setIcon(self.tray_icon)
        else:
            print("Icon and tray icon have not been set.")
        if self.tray_menu_items:
            pass
        else:
            self.tray.setContextMenu(QMenu())
        self.tray.show()

    def _update_tray_menu(self):
        """Updates the tray menu."""
        tray_menu = self.tray.contextMenu()
        tray_menu.clear()
        for item in self.tray_menu_items:
            action = QAction(item["label"], self)
            action.triggered.connect(item["callback"])
            tray_menu.addAction(action)

    def _tray_activated(self, reason):
        """Handles events when the tray icon is activated."""
        reason_enum = QSystemTrayIcon.ActivationReason(reason)

        if reason_enum in self.tray_actions:
            self.tray_actions[reason_enum]()

    def set_tray_actions(self, actions):
        """
        Dynamically sets actions for tray icon activation.
        Can be called while the application is running, and changes are applied immediately.

        :param actions: Dictionary with TrayEvent enum values as keys and corresponding callback functions as values
        """
        if self.tray_actions:
            self.tray.activated.disconnect()  # Disconnect existing connections

        self.tray_actions = actions
        if not hasattr(self, "tray"):
            self._init_tray()

        self.tray.activated.connect(lambda reason: self._tray_activated(reason))

    def show_notification(self, title: str, message: str):
        """
        Displays a notification in the system tray.
        Can be called while the application is running, and the notification is displayed immediately.

        :param title: Notification title
        :param message: Notification content
        """
        if not hasattr(self, "tray"):
            self._init_tray()  # Ensure the tray is initialized

        self.tray.showMessage(title, message, QIcon(self.icon), 5000)

    def _update_tray_icon(self):
        """Updates the animation frames."""
        if hasattr(self, "tray") and self.icon_frames:
            self.tray.setIcon(self.icon_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.icon_frames)

    def set_tray_icon_animation(self, icon_frames: List[str], interval: int = 200):
        """
        Dynamically sets and starts an animation for the tray icon.
        Can be called while the application is running, and changes are applied immediately.

        :param icon_frames: List of paths to animation frame images
        :param interval: Interval between frames (milliseconds)
        """
        if not hasattr(self, "tray"):
            self._init_tray()

        # Remove existing icon
        if hasattr(self, "tray_icon"):
            del self.tray_icon

        # Stop and remove existing animation timer
        if hasattr(self, "animation_timer") and self.animation_timer is not None:
            self.animation_timer.stop()
            self.animation_timer.deleteLater()
            self.animation_timer = None

        self.icon_frames = [QIcon(frame) for frame in icon_frames]
        self.animation_interval = interval
        self.start_tray_icon_animation()

    def start_tray_icon_animation(self):
        """Starts the tray icon animation."""
        if self.icon_frames:
            if self.animation_timer is None:
                self.animation_timer = QTimer(self)
                self.animation_timer.timeout.connect(lambda: self._update_tray_icon())
            self.animation_timer.start(self.animation_interval)
            self.current_frame = 0

    def set_tray_tooltip(self, message: str):
        """
        Dynamically sets the tooltip for the tray icon.
        Can be called while the application is running, and changes are applied immediately.

        :param message: New tooltip message
        """
        if not hasattr(self, "tray"):
            self._init_tray()
        self.tray.setToolTip(message)

    def set_notification_callback(self, callback: Callable[[str], None]):
        """
        Sets the callback function to be called when a notification is clicked.

        :param callback: Callback function to be called when a notification is clicked
        """
        if not hasattr(self, "tray"):
            self._init_tray()
        self.tray.messageClicked.connect(callback)

    ###########################################################################################
    # Monitor
    ###########################################################################################
    def get_all_monitors(self) -> List[Monitor]:
        """
        Returns a list of information for all connected monitors.

        :return: List containing monitor information
        """
        monitors = [
            Monitor(index, screen) for index, screen in enumerate(self.screens())
        ]
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
            print(
                "\033[93mset_auto_start(True) is not supported in non-production environment\033[0m"
            )
            return None

    def is_auto_start(self):
        """
        Checks if the application is set to start automatically with the system.

        :return: True if auto-start is enabled, False otherwise
        """

        return self.auto_start.is_auto_start()

    ###########################################################################################
    # File watcher
    ###########################################################################################
    def watch_file(self, file_path: str) -> bool:
        """
        Adds a file to the watch list.

        :param file_path: Path of the file to watch
        :return: True if the file was successfully added to the watch list, False otherwise
        """
        return self.file_watcher.add_path(file_path)

    def watch_directory(self, dir_path: str) -> bool:
        """
        Adds a directory to the watch list.

        :param dir_path: Path of the directory to watch
        :return: True if the directory was successfully added to the watch list, False otherwise
        """
        return self.file_watcher.add_path(dir_path)

    def stop_watching(self, path: str) -> bool:
        """
        Removes a file or directory from the watch list.

        :param path: Path of the file or directory to stop watching
        :return: True if the path was successfully removed from the watch list, False otherwise
        """
        return self.file_watcher.remove_path(path)

    def get_watched_paths(self) -> List[str]:
        """
        Returns all currently watched paths.

        :return: List of all watched paths
        """
        return self.file_watcher.get_watched_paths()

    def get_watched_files(self) -> List[str]:
        """
        Returns all currently watched files.

        :return: List of all watched files
        """
        return self.file_watcher.get_watched_files()

    def get_watched_directories(self) -> List[str]:
        """
        Returns all currently watched directories.

        :return: List of all watched directories
        """
        return self.file_watcher.get_watched_directories()

    def remove_all_watched_paths(self) -> None:
        """
        Removes all paths from the watch list.

        :return: None
        """
        self.file_watcher.remove_all_paths()

    def set_file_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to be called when a file changes.

        :param callback: Function to be called when a file changes
        """
        self.file_watcher.file_changed.connect(callback)

    def set_directory_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to be called when a directory changes.

        :param callback: Function to be called when a directory changes
        """
        self.file_watcher.directory_changed.connect(callback)
