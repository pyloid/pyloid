import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QFileDialog,
)
from PySide6.QtGui import (
    QIcon,
    QClipboard,
    QImage,
    QAction,
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QEvent
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from .api import PyloidAPI
from typing import List, Optional, Dict, Callable, Union, Literal
from PySide6.QtCore import qInstallMessageHandler
import signal
from .utils import is_production
from .monitor import Monitor
from .autostart import AutoStart
from .filewatcher import FileWatcher
import logging
from .browser_window import BrowserWindow
from .tray import TrayEvent
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Signal, QObject, Slot
import uuid
from PySide6.QtCore import QEventLoop
import socket
from typing import Any

# for linux debug
os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = "/"

# for macos debug
logging.getLogger("Qt").setLevel(logging.ERROR)

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--enable-features=WebRTCPipeWireCapturer --ignore-certificate-errors --allow-insecure-localhost"
)


def custom_message_handler(mode, context, message):
    if not hasattr(custom_message_handler, "vulkan_warning_shown") and (
        ("Failed to load vulkan" in message)
        or ("No Vulkan library available" in message)
        or ("Failed to create platform Vulkan instance" in message)
    ):
        print(
            "\033[93mPyloid Warning: Vulkan GPU API issue detected. Switching to software backend.\033[0m"
        )
        if "linux" in sys.platform:
            os.environ["QT_QUICK_BACKEND"] = "software"
            custom_message_handler.vulkan_warning_shown = True

    if "Autofill.enable failed" in message:
        print(
            "\033[93mPyloid Warning: Autofill is not enabled in developer tools.\033[0m"
        )

    if "vulkan" not in message.lower() and "Autofill.enable failed" not in message:
        print(message)


qInstallMessageHandler(custom_message_handler)


class _WindowController(QObject):
    create_window_signal = Signal(
        QApplication, str, int, int, int, int, bool, bool, bool, list
    )



# Only Work in Main Thread
class _Pyloid(QApplication):
    def __init__(
        self,
        app_name,
        single_instance=True,
        data=None,
    ):
        """
        Initializes the Pyloid application.

        Parameters
        ----------
        app_name : str, required
            The name of the application
        single_instance : bool, optional
            Whether to run the application as a single instance (default is True)
        data : dict, optional
            Data to be transmitted to the frontend web engine via IPC

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="New Window", width=1024, height=768)
        window.show()

        app.run()
        ```
        """
        super().__init__(sys.argv)
        
        self.data = data

        self.windows_dict = {}  # 윈도우 ID를 키로 사용하는 딕셔너리
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

        self.theme = (
            "dark"
            if self.styleHints().colorScheme() == Qt.ColorScheme.Dark
            else "light"
        )

        # Add color scheme tracking
        self.styleHints().colorSchemeChanged.connect(self._handle_color_scheme_change)

    # def set_theme(self, theme: Literal["system", "dark", "light"]):
    #     """
    #     시스템의 테마를 설정합니다.

    #     Parameters
    #     ----------
    #     theme : Literal["system", "dark", "light"]
    #         설정할 테마 ("system", "dark", "light" 중 하나)

    #     Examples
    #     --------
    #     >>> app = Pyloid(app_name="Pyloid-App")
    #     >>> app.set_theme("dark")  # 다크 테마로 설정
    #     >>> app.set_theme("light")  # 라이트 테마로 설정
    #     >>> app.set_theme("system")  # 시스템 테마를 따름
    #     """
    #     self.theme = theme

    #     if theme == "system":
    #         # 시스템 테마를 light/dark 문자열로 변환
    #         system_theme = (
    #             "dark"
    #             if self.styleHints().colorScheme() == Qt.ColorScheme.Dark
    #             else "light"
    #         )
    #         self._handle_color_scheme_change(system_theme)
    #         self.styleHints().colorSchemeChanged.connect(
    #             lambda: self._handle_color_scheme_change(system_theme)
    #         )
    #     else:
    #         # 기존 이벤트 연결 해제
    #         self.styleHints().colorSchemeChanged.disconnect(
    #             lambda: self._handle_color_scheme_change(self.theme)
    #         )
    #         self._handle_color_scheme_change(self.theme)

    def set_icon(self, icon_path: str):
        """
        Dynamically sets the application's icon.

        This method can be called while the application is running.
        The icon can be changed at any time and will be applied immediately.

        Parameters
        ----------
        icon_path : str
            Path to the new icon file

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_icon("icons/icon.png")
        """
        self.icon = QIcon(icon_path)

        # Immediately update the icon for all open windows.
        for window in self.windows_dict.values():
            window.set_icon(self.icon)

    def create_window(
        self,
        title: str,
        width: int = 800,
        height: int = 600,
        x: int = 200,
        y: int = 200,
        frame: bool = True,
        context_menu: bool = False,
        dev_tools: bool = False,
        js_apis: List[PyloidAPI] = [],
    ) -> BrowserWindow:
        """
        Creates a new browser window.

        Parameters
        ----------
        title : str, required
            Title of the window
        width : int, optional
            Width of the window (default is 800)
        height : int, optional
            Height of the window (default is 600)
        x : int, optional
            X coordinate of the window (default is 200)
        y : int, optional
            Y coordinate of the window (default is 200)
        frame : bool, optional
            Whether the window has a frame (default is True)
        context_menu : bool, optional
            Whether to use the context menu (default is False)
        dev_tools : bool, optional
            Whether to use developer tools (default is False)
        js_apis : list of PyloidAPI, optional
            List of JavaScript APIs to add to the window (default is an empty list)

        Returns
        -------
        BrowserWindow
            The created browser window object

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window(title="New Window", width=1024, height=768)
        >>> window.show()
        """
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
        latest_window_id = list(self.windows_dict.keys())[-1]
        return self.windows_dict[latest_window_id]

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
        self.windows_dict[window.window.id] = window
        return window

    def run(self):
        """
        Runs the application event loop.

        This method starts the application's event loop, allowing the application to run.

        This code should be written at the very end of the file.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        app.run()
        ```
        """
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
    def get_windows(self) -> Dict[str, BrowserWindow]:
        """
        Returns a list of all browser windows.

        Returns
        -------
        List[BrowserWindow]
            List of all browser windows

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        windows = app.get_windows()
        for window in windows:
            print(window.get_id())
        ```
        """
        return self.windows_dict

    def show_main_window(self):
        """
        Shows and focuses the first window.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        app.show_main_window()
        ```
        """
        if self.windows_dict:
            # 첫 번째 윈도우 가져오기
            main_window = next(iter(self.windows_dict.values()))
            main_window._window.show()

    def focus_main_window(self):
        """
        Focuses the first window.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        app.focus_main_window()
        ```
        """
        if self.windows_dict:
            # 첫 번째 윈도우 가져오기
            main_window = next(iter(self.windows_dict.values()))
            main_window._window.activateWindow()
            main_window._window.raise_()
            main_window._window.setWindowState(
                main_window._window.windowState() & ~Qt.WindowMinimized
                | Qt.WindowActive
            )

    def show_and_focus_main_window(self):
        """
        Shows and focuses the first window.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        app.show_and_focus_main_window()
        ```
        """
        if self.windows_dict:
            # 첫 번째 윈도우 가져오기
            main_window = next(iter(self.windows_dict.values()))
            main_window._window.show()
            main_window._window.activateWindow()
            main_window._window.raise_()
            main_window._window.setWindowState(
                main_window._window.windowState() & ~Qt.WindowMinimized
                | Qt.WindowActive
            )

    def close_all_windows(self):
        """
        Closes all windows.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        app.close_all_windows()
        ```
        """
        for window in self.windows_dict.values():
            window._window.close()

    def quit(self):
        """
        Quits the application.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        app.quit()
        ```
        """
        
        # 윈도우 정리
        for window in self.windows_dict.values():
            window._window.close()
            window.web_page.deleteLater()
            window.web_view.deleteLater()

        # 딕셔너리 비우기
        self.windows_dict.clear()
        QApplication.quit()

    ###########################################################################################
    # Window management in the app (ID required)
    ###########################################################################################
    def get_window_by_id(self, window_id: str) -> Optional[BrowserWindow]:
        """
        Returns the window with the given ID.
        
        Parameters
        ----------
        window_id : str
            The ID of the window to find

        Returns
        -------
        Optional[BrowserWindow]
            The window object with the given ID. Returns None if the window is not found.
        
        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")
        
        window = app.get_window_by_id("123e4567-e89b-12d3-a456-426614174000")
        
        if window:
            print("Window found:", window)
        ```
        """
        return self.windows_dict.get(window_id)

    def hide_window_by_id(self, window_id: str):
        """
        Hides the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to hide

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.hide_window_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        if window:
            window.hide()

    def show_window_by_id(self, window_id: str):
        """
        Shows and focuses the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to show

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.show_window_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        if window:
            window.show()

    def close_window_by_id(self, window_id: str):
        """
        Closes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to close

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.close_window_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        if window:
            window._window.close()

    def toggle_fullscreen_by_id(self, window_id: str):
        """
        Toggles fullscreen mode for the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to toggle fullscreen mode

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.toggle_fullscreen_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        window.toggle_fullscreen()

    def minimize_window_by_id(self, window_id: str):
        """
        Minimizes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to minimize

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.minimize_window_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        if window:
            window.minimize()

    def maximize_window_by_id(self, window_id: str):
        """
        Maximizes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to maximize

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.maximize_window_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        if window:
            window.maximize()

    def unmaximize_window_by_id(self, window_id: str):
        """
        Unmaximizes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to unmaximize

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        app.unmaximize_window_by_id(window.id)
        ```
        """
        window = self.get_window_by_id(window_id)
        if window:
            window.unmaximize()

    def capture_window_by_id(self, window_id: str, save_path: str) -> Optional[str]:
        """
        Captures the specified window.

        Parameters
        ----------
        window_id : str
            The ID of the window to capture
        save_path : str
            The path to save the captured image. If not specified, it will be saved in the current directory.

        Returns
        -------
        Optional[str]
            The path of the saved image. Returns None if the window is not found or an error occurs.

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window(title="pyloid-window")

        image_path = app.capture_window_by_id(window.id, "save/image.png")

        if image_path:
            print("Image saved at:", image_path)
        ```
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

        Parameters
        ----------
        tray_icon_path : str
            The path of the new tray icon file

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_icon("icons/icon.png")
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

        Parameters
        ----------
        tray_menu_items : List[Dict[str, Union[str, Callable]]]
            The list of new tray menu items

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> menu_items = [
        >>>     {"label": "Open", "callback": lambda: print("Open clicked")},
        >>>     {"label": "Exit", "callback": app.quit}
        >>> ]
        >>> app.set_tray_menu_items(menu_items)
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

    def set_tray_actions(self, actions: Dict[TrayEvent, Callable]):
        """
        Dynamically sets the actions for tray icon activation.
        Can be called while the application is running, and changes are applied immediately.

        Parameters
        ----------
        actions: Dict[TrayEvent, Callable]
            Dictionary with TrayEvent enum values as keys and corresponding callback functions as values

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_actions(
        >>>    {
        >>>        TrayEvent.DoubleClick: lambda: print("Tray icon was double-clicked."),
        >>>        TrayEvent.MiddleClick: lambda: print("Tray icon was middle-clicked."),
        >>>        TrayEvent.RightClick: lambda: print("Tray icon was right-clicked."),
        >>>        TrayEvent.LeftClick: lambda: print("Tray icon was left-clicked."),
        >>>    }
        >>> )
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

        Parameters
        ----------
        title : str
            Notification title
        message : str
            Notification message

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.show_notification("Update Available", "A new update is available for download.")
        """
        if not hasattr(self, "tray"):
            self._init_tray()  # Ensure the tray is initialized

        self.tray.showMessage(title, message, QIcon(self.icon), 5000)

    def _update_tray_icon(self):
        """
        Updates the animation frame.
        """
        if hasattr(self, "tray") and self.icon_frames:
            self.tray.setIcon(self.icon_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.icon_frames)

    def set_tray_icon_animation(self, icon_frames: List[str], interval: int = 200):
        """
        Dynamically sets and starts the animation for the tray icon.
        Can be called while the application is running, and changes are applied immediately.

        Parameters
        ----------
        icon_frames : list of str
            List of animation frame image paths
        interval : int, optional
            Frame interval in milliseconds, default is 200

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> icon_frames = ["frame1.png", "frame2.png", "frame3.png"]
        >>> app.set_tray_icon_animation(icon_frames, 100)
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
        self._start_tray_icon_animation()

    def _start_tray_icon_animation(self):
        """
        Starts the tray icon animation.
        """
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

        Parameters
        ----------
        message : str
            New tooltip message

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_tooltip("Pyloid is running")
        """
        if not hasattr(self, "tray"):
            self._init_tray()
        self.tray.setToolTip(message)

    def set_notification_callback(self, callback: Callable[[str], None]):
        """
        Sets the callback function to be called when a notification is clicked.

        Parameters
        ----------
        callback : function
            Callback function to be called when a notification is clicked

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> def on_notification_click():
        >>>     print("Notification clicked")
        >>> app.set_notification_callback(on_notification_click)
        """
        if not hasattr(self, "tray"):
            self._init_tray()
        self.tray.messageClicked.connect(callback)

    ###########################################################################################
    # Monitor
    ###########################################################################################
    def get_all_monitors(self) -> List[Monitor]:
        """
        Returns information about all connected monitors.

        Returns
        -------
        list of Monitor
            List containing monitor information

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> monitors = app.get_all_monitors()
        >>> for monitor in monitors:
        >>>     print(monitor.info())
        """
        monitors = [
            Monitor(index, screen) for index, screen in enumerate(self.screens())
        ]
        return monitors

    def get_primary_monitor(self) -> Monitor:
        """
        Returns information about the primary monitor.

        Returns
        -------
        Monitor
            Primary monitor information

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> primary_monitor = app.get_primary_monitor()
        >>> print(primary_monitor.info())
        """
        primary_monitor = self.screens()[0]
        return Monitor(0, primary_monitor)

    ###########################################################################################
    # Clipboard
    ###########################################################################################
    def set_clipboard_text(self, text):
        """
        Copies text to the clipboard.

        This function copies the given text to the clipboard. The text copied to the clipboard can be pasted into other applications.

        Parameters
        ----------
        text : str
            Text to copy to the clipboard

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_clipboard_text("Hello, World!")
        """
        self.clipboard_class.setText(text, QClipboard.Clipboard)

    def get_clipboard_text(self):
        """
        Retrieves text from the clipboard.

        This function returns the text stored in the clipboard. If there is no text in the clipboard, it may return an empty string.

        Returns
        -------
        str
            Text stored in the clipboard

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> text = app.get_clipboard_text()
        >>> print(text)
        Hello, World!
        """
        return self.clipboard_class.text()

    def set_clipboard_image(self, image: Union[str, bytes, os.PathLike]):
        """
        Copies an image to the clipboard.

        This function copies the given image file to the clipboard. The image copied to the clipboard can be pasted into other applications.

        Parameters
        ----------
        image : Union[str, bytes, os.PathLike]
            Path to the image file to copy to the clipboard

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_clipboard_image("/path/to/image.png")
        """
        self.clipboard_class.setImage(QImage(image), QClipboard.Clipboard)

    def get_clipboard_image(self):
        """
        Retrieves an image from the clipboard.

        This function returns the image stored in the clipboard. If there is no image in the clipboard, it may return None.

        Returns
        -------
        QImage
            QImage object stored in the clipboard (None if no image)

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> image = app.get_clipboard_image()
        >>> if image is not None:
        >>>     image.save("/path/to/save/image.png")
        """
        return self.clipboard_class.image()

    ###########################################################################################
    # Autostart
    ###########################################################################################
    def set_auto_start(self, enable: bool):
        """
        Sets the application to start automatically at system startup. (set_auto_start(True) only works in production environment)
        True only works in production environment.
        False works in all environments.

        Parameters
        ----------
        enable : bool
            True to enable auto start, False to disable

        Returns
        -------
        bool or None
            True if auto start is successfully set, False if disabled, None if trying to enable in non-production environment

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_auto_start(True)
        True
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
        Checks if the application is set to start automatically at system startup.

        Returns
        -------
        bool
            True if auto start is enabled, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> auto_start_enabled = app.is_auto_start()
        >>> print(auto_start_enabled)
        True
        """
        return self.auto_start.is_auto_start()

    ###########################################################################################
    # File watcher
    ###########################################################################################
    def watch_file(self, file_path: str) -> bool:
        """
        Adds a file to the watch list.

        This function adds the specified file to the watch list. When the file is changed, the set callback function is called.

        Parameters
        ----------
        file_path : str
            Path to the file to watch

        Returns
        -------
        bool
            True if the file is successfully added to the watch list, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.watch_file("/path/to/file.txt")
        True
        """
        return self.file_watcher.add_path(file_path)

    def watch_directory(self, dir_path: str) -> bool:
        """
        Adds a directory to the watch list.

        This function adds the specified directory to the watch list. When a file in the directory is changed, the set callback function is called.

        Parameters
        ----------
        dir_path : str
            Path to the directory to watch

        Returns
        -------
        bool
            True if the directory is successfully added to the watch list, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.watch_directory("/path/to/directory")
        True
        """
        return self.file_watcher.add_path(dir_path)

    def stop_watching(self, path: str) -> bool:
        """
        Removes a file or directory from the watch list.

        This function removes the specified file or directory from the watch list.

        Parameters
        ----------
        path : str
            Path to the file or directory to stop watching

        Returns
        -------
        bool
            True if the path is successfully removed from the watch list, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.stop_watching("/path/to/file_or_directory")
        True
        """
        return self.file_watcher.remove_path(path)

    def get_watched_paths(self) -> List[str]:
        """
        Returns all currently watched paths.

        This function returns the paths of all files and directories currently being watched.

        Returns
        -------
        List[str]
            List of all watched paths

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.get_watched_paths()
        ['/path/to/file1.txt', '/path/to/directory']
        """
        return self.file_watcher.get_watched_paths()

    def get_watched_files(self) -> List[str]:
        """
        Returns all currently watched files.

        This function returns the paths of all files currently being watched.

        Returns
        -------
        List[str]
            List of all watched files

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.get_watched_files()
        ['/path/to/file1.txt', '/path/to/file2.txt']
        """
        return self.file_watcher.get_watched_files()

    def get_watched_directories(self) -> List[str]:
        """
        Returns all currently watched directories.

        This function returns the paths of all directories currently being watched.

        Returns
        -------
        List[str]
            List of all watched directories

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.get_watched_directories()
        ['/path/to/directory1', '/path/to/directory2']
        """
        return self.file_watcher.get_watched_directories()

    def remove_all_watched_paths(self) -> None:
        """
        Removes all paths from the watch list.

        This function removes the paths of all files and directories from the watch list.

        Returns
        -------
        None

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.remove_all_watched_paths()
        """
        self.file_watcher.remove_all_paths()

    def set_file_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to be called when a file is changed.

        This function sets the callback function to be called when a file is changed.

        Parameters
        ----------
        callback : Callable[[str], None]
            Function to be called when a file is changed

        Returns
        -------
        None

        Examples
        --------
        >>> def on_file_change(file_path):
        >>>     print(f"File changed: {file_path}")
        >>>
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_file_change_callback(on_file_change)
        """
        self.file_watcher.file_changed.connect(callback)

    def set_directory_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to be called when a directory is changed.

        This function sets the callback function to be called when a directory is changed.

        Parameters
        ----------
        callback : Callable[[str], None]
            Function to be called when a directory is changed

        Returns
        -------
        None

        Examples
        --------
        >>> def on_directory_change(dir_path):
        >>>     print(f"Directory changed: {dir_path}")
        >>>
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_directory_change_callback(on_directory_change)
        """
        self.file_watcher.directory_changed.connect(callback)

    ###########################################################################################
    # File dialog
    ###########################################################################################
    def open_file_dialog(
        self, dir: Optional[str] = None, filter: Optional[str] = None
    ) -> Optional[str]:
        """
        Opens a file dialog to select a file to open.

        Parameters
        ----------
        dir : str, optional
            The initial directory that the dialog will open in. If None, the dialog will open in the current working directory.
        filter : str, optional
            A string that specifies the file types that can be selected. For example, "Text Files (*.txt);;All Files (*)".

        Returns
        -------
        Optional[str]
            The path of the selected file. Returns None if no file is selected.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> file_path = app.open_file_dialog(dir="/home/user", filter="Text Files (*.txt)")
        >>> if file_path:
        >>>     print("Selected file:", file_path)
        """
        file_path, _ = QFileDialog.getOpenFileName(None, dir=dir, filter=filter)
        return file_path if file_path else None

    def save_file_dialog(
        self, dir: Optional[str] = None, filter: Optional[str] = None
    ) -> Optional[str]:
        """
        Opens a file dialog to select a file to save.

        Parameters
        ----------
        dir : str, optional
            The initial directory that the dialog will open in. If None, the dialog will open in the current working directory.
        filter : str, optional
            A string that specifies the file types that can be saved. For example, "Text Files (*.txt);;All Files (*)".

        Returns
        -------
        Optional[str]
            The path of the selected file. Returns None if no file is selected.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> file_path = app.save_file_dialog(dir="/home/user", filter="Text Files (*.txt)")
        >>> if file_path:
        >>>     print("File will be saved to:", file_path)
        """
        file_path, _ = QFileDialog.getSaveFileName(None, dir=dir, filter=filter)
        return file_path if file_path else None

    def select_directory_dialog(self, dir: Optional[str] = None) -> Optional[str]:
        """
        Opens a dialog to select a directory.

        Parameters
        ----------
        dir : str, optional
            The initial directory that the dialog will open in. If None, the dialog will open in the current working directory.

        Returns
        -------
        Optional[str]
            The path of the selected directory. Returns None if no directory is selected.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> directory_path = app.select_directory_dialog(dir="/home/user")
        >>> if directory_path:
        >>>     print("Selected directory:", directory_path)
        """
        directory_path = QFileDialog.getExistingDirectory(None, dir=dir)
        return directory_path if directory_path else None

    def _handle_color_scheme_change(self):
        self.theme = (
            "dark"
            if self.styleHints().colorScheme() == Qt.ColorScheme.Dark
            else "light"
        )

        js_code = f"""
        document.dispatchEvent(new CustomEvent('themeChange', {{ 
            detail: {{ theme: "{self.theme}" }} 
        }}));
        """

        # 모든 윈도우에 변경사항 적용
        for window in self.windows_dict.values():
            window.web_view.page().runJavaScript(js_code)
            window.web_view.page().setBackgroundColor(
                Qt.GlobalColor.black if self.theme == "dark" else Qt.GlobalColor.white
            )
            

class Pyloid(QObject):
    command_signal = Signal(str, str, object)
    result_signal = Signal(str, object)
    
    def __init__(self, app_name: str, single_instance: bool = True, data: Optional[Dict[str, Any]] = None):
        """
        Initialize the Pyloid application.

        This application is designed to work in a multi-threaded environment.
        All Qt GUI related operations are executed in the main thread's event queue regardless of the calling thread,
        ensuring thread safety for GUI operations.

        Parameters
        ----------
        app_name : str, required
            The name of the application.
        single_instance : bool, optional
            Determines whether to run as a single instance. (Default is True)
        data : dict, optional
            Data to be transmitted to the frontend web engine via IPC

        Notes
        -----
        The generated or passed `id` is transmitted to the frontend via IPC,
        and is used as an API key to connect to the integrated backend FastAPI server.
        """
        super().__init__()
        
        self.data = data

        self.app = _Pyloid(app_name, single_instance, self.data)
        
        self.command_signal.connect(self._handle_command)
    
    @Slot(str, str, object)
    def _handle_command(self, command_id, command_type, params):
        result = None

        if command_type == "set_icon":
            result = self.app.set_icon(params["icon_path"])

        elif command_type == "create_window":
            window = self.app.create_window(
                title=params.get("title", ""),
                width=params.get("width", 800),
                height=params.get("height", 600),
                x=params.get("x", 200),
                y=params.get("y", 200),
                frame=params.get("frame", True),
                context_menu=params.get("context_menu", False),
                dev_tools=params.get("dev_tools", False)
            )
            result = window

        elif command_type == "run":
            result = self.app.run()

        elif command_type == "get_windows":
            result = self.app.get_windows()

        elif command_type == "show_main_window":
            result = self.app.show_main_window()

        elif command_type == "focus_main_window":
            result = self.app.focus_main_window()

        elif command_type == "show_and_focus_main_window":
            result = self.app.show_and_focus_main_window()

        elif command_type == "close_all_windows":
            result = self.app.close_all_windows()

        elif command_type == "quit":
            result = self.app.quit()

        elif command_type == "get_window_by_id":
            result = self.app.get_window_by_id(params["window_id"])

        elif command_type == "hide_window_by_id":
            result = self.app.hide_window_by_id(params["window_id"])

        elif command_type == "show_window_by_id":
            result = self.app.show_window_by_id(params["window_id"])

        elif command_type == "close_window_by_id":
            result = self.app.close_window_by_id(params["window_id"])

        elif command_type == "toggle_fullscreen_by_id":
            result = self.app.toggle_fullscreen_by_id(params["window_id"])

        elif command_type == "minimize_window_by_id":
            result = self.app.minimize_window_by_id(params["window_id"])

        elif command_type == "maximize_window_by_id":
            result = self.app.maximize_window_by_id(params["window_id"])

        elif command_type == "unmaximize_window_by_id":
            result = self.app.unmaximize_window_by_id(params["window_id"])

        elif command_type == "capture_window_by_id":
            result = self.app.capture_window_by_id(params["window_id"], params["save_path"])

        elif command_type == "set_tray_icon":
            result = self.app.set_tray_icon(params["tray_icon_path"])

        elif command_type == "set_tray_menu_items":
            result = self.app.set_tray_menu_items(params["tray_menu_items"])

        elif command_type == "set_tray_actions":
            result = self.app.set_tray_actions(params["actions"])

        elif command_type == "show_notification":
            result = self.app.show_notification(params["title"], params["message"])

        elif command_type == "set_tray_icon_animation":
            result = self.app.set_tray_icon_animation(params["icon_frames"], params.get("interval", 200))

        elif command_type == "set_tray_tooltip":
            result = self.app.set_tray_tooltip(params["message"])

        elif command_type == "set_notification_callback":
            result = self.app.set_notification_callback(params["callback"])

        elif command_type == "get_all_monitors":
            result = self.app.get_all_monitors()

        elif command_type == "get_primary_monitor":
            result = self.app.get_primary_monitor()

        elif command_type == "set_clipboard_text":
            result = self.app.set_clipboard_text(params["text"])

        elif command_type == "get_clipboard_text":
            result = self.app.get_clipboard_text()

        elif command_type == "set_clipboard_image":
            result = self.app.set_clipboard_image(params["image"])

        elif command_type == "get_clipboard_image":
            result = self.app.get_clipboard_image()

        elif command_type == "set_auto_start":
            result = self.app.set_auto_start(params["enable"])

        elif command_type == "is_auto_start":
            result = self.app.is_auto_start()

        elif command_type == "watch_file":
            result = self.app.watch_file(params["file_path"])

        elif command_type == "watch_directory":
            result = self.app.watch_directory(params["dir_path"])

        elif command_type == "stop_watching":
            result = self.app.stop_watching(params["path"])

        elif command_type == "get_watched_paths":
            result = self.app.get_watched_paths()

        elif command_type == "get_watched_files":
            result = self.app.get_watched_files()

        elif command_type == "get_watched_directories":
            result = self.app.get_watched_directories()

        elif command_type == "remove_all_watched_paths":
            result = self.app.remove_all_watched_paths()

        elif command_type == "set_file_change_callback":
            result = self.app.set_file_change_callback(params["callback"])

        elif command_type == "set_directory_change_callback":
            result = self.app.set_directory_change_callback(params["callback"])

        elif command_type == "open_file_dialog":
            result = self.app.open_file_dialog(params.get("dir"), params.get("filter"))

        elif command_type == "save_file_dialog":
            result = self.app.save_file_dialog(params.get("dir"), params.get("filter"))

        elif command_type == "select_directory_dialog":
            result = self.app.select_directory_dialog(params.get("dir"))

        else:
            return None

        self.result_signal.emit(command_id, result)
    
    def execute_command(self, command_type: str, params: object, timeout: Optional[int] = None):
        command_id = str(uuid.uuid4())
        
        result_data = [None]
        loop = QEventLoop()
        
        if timeout:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            timer.start(timeout)
        
        def on_result(received_id, result):
            if received_id == command_id:
                result_data[0] = result     
                loop.quit()

        
        self.result_signal.connect(on_result, Qt.QueuedConnection)
        
        self.command_signal.emit(command_id, command_type, params)
                
        loop.exec()
                
        self.result_signal.disconnect(on_result)
        
        return result_data[0]
    
    # -------------------------------------------------------------------
    # Execute_command 래퍼 (wrapper) 함수들
    # -------------------------------------------------------------------
    
    def set_icon(self, icon_path: str) -> bool:
        """
        Dynamically sets the application's icon.

        Parameters
        ----------
        icon_path : str
            Path to the new icon file

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_icon("icons/icon.png")
        """
        return self.execute_command("set_icon", {"icon_path": icon_path})
    
    def create_window(
        self,
        title: str,
        width: int = 800,
        height: int = 600,
        x: int = 200,
        y: int = 200,
        frame: bool = True,
        context_menu: bool = False,
        dev_tools: bool = False,
    ) -> BrowserWindow:
        """
        Creates a new browser window.

        Parameters
        ----------
        title : str, required
            Title of the window
        width : int, optional
            Width of the window (default is 800)
        height : int, optional
            Height of the window (default is 600)
        x : int, optional
            X coordinate of the window (default is 200)
        y : int, optional
            Y coordinate of the window (default is 200)
        frame : bool, optional
            Whether the window has a frame (default is True)
        context_menu : bool, optional
            Whether to use the context menu (default is False)
        dev_tools : bool, optional
            Whether to use developer tools (default is False)

        Returns
        -------
        BrowserWindow
            The created browser window object

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window_id = app.create_window(title="New Window", width=1024, height=768)
        """
        params = {
            "title": title,
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "frame": frame,
            "context_menu": context_menu,
            "dev_tools": dev_tools,
        }
        return self.execute_command("create_window", params)
    
    def run(self) -> None:
        """
        Runs the application event loop.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.run()
        """
        return self.app.run()
    
    def get_windows(self) -> Dict[str, BrowserWindow]:
        """
        Returns a list of all browser windows.

        Returns
        -------
        Dict[str, BrowserWindow]
            Dictionary of all browser windows

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> windows = app.get_windows()
        """
        return self.execute_command("get_windows", {})
    
    def show_main_window(self) -> None:
        """
        Shows and focuses the first window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.show_main_window()
        """
        return self.execute_command("show_main_window", {})
    
    def focus_main_window(self) -> None:
        """
        Focuses the first window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.focus_main_window()
        """
        return self.execute_command("focus_main_window", {})
    
    def show_and_focus_main_window(self) -> None:
        """
        Shows and focuses the first window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.show_and_focus_main_window()
        """
        return self.execute_command("show_and_focus_main_window", {})
    
    def close_all_windows(self) -> None:
        """
        Closes all windows.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.close_all_windows()
        """
        return self.execute_command("close_all_windows", {})
    
    def quit(self) -> None:
        """
        Quits the application.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.quit()
        """
        return self.execute_command("quit", {})
    
    def get_window_by_id(self, window_id: str) -> Optional[BrowserWindow]:
        """
        Returns the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to find

        Returns
        -------
        Optional[BrowserWindow]
            The window object with the given ID. Returns None if the window is not found.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.get_window_by_id("some-window-id")
        """
        return self.execute_command("get_window_by_id", {"window_id": window_id})
    
    def hide_window_by_id(self, window_id: str) -> None:
        """
        Hides the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to hide

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.hide_window_by_id("some-window-id")
        """
        return self.execute_command("hide_window_by_id", {"window_id": window_id})
    
    def show_window_by_id(self, window_id: str) -> None:
        """
        Shows and focuses the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to show

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.show_window_by_id("some-window-id")
        """
        return self.execute_command("show_window_by_id", {"window_id": window_id})
    
    def close_window_by_id(self, window_id: str) -> None:
        """
        Closes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to close

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.close_window_by_id("some-window-id")
        """
        return self.execute_command("close_window_by_id", {"window_id": window_id})
    
    def toggle_fullscreen_by_id(self, window_id: str) -> None:
        """
        Toggles fullscreen mode for the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to toggle fullscreen mode

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.toggle_fullscreen_by_id("some-window-id")
        """
        return self.execute_command("toggle_fullscreen_by_id", {"window_id": window_id})
    
    def minimize_window_by_id(self, window_id: str) -> None:
        """
        Minimizes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to minimize

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.minimize_window_by_id("some-window-id")
        """
        return self.execute_command("minimize_window_by_id", {"window_id": window_id})
    
    def maximize_window_by_id(self, window_id: str) -> None:
        """
        Maximizes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to maximize

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.maximize_window_by_id("some-window-id")
        """
        return self.execute_command("maximize_window_by_id", {"window_id": window_id})
    
    def unmaximize_window_by_id(self, window_id: str) -> None:
        """
        Unmaximizes the window with the given ID.

        Parameters
        ----------
        window_id : str
            The ID of the window to unmaximize

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.unmaximize_window_by_id("some-window-id")
        """
        return self.execute_command("unmaximize_window_by_id", {"window_id": window_id})
    
    def capture_window_by_id(self, window_id: str, save_path: str) -> Optional[str]:
        """
        Captures the specified window.

        Parameters
        ----------
        window_id : str
            The ID of the window to capture
        save_path : str
            The path to save the captured image

        Returns
        -------
        Optional[str]
            The path of the saved image. Returns None if the window is not found or an error occurs.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> image_path = app.capture_window_by_id("some-window-id", "save/image.png")
        """
        return self.execute_command("capture_window_by_id", {"window_id": window_id, "save_path": save_path})
    
    def set_tray_icon(self, tray_icon_path: str) -> bool:
        """
        Dynamically sets the tray icon.

        Parameters
        ----------
        tray_icon_path : str
            The path of the new tray icon file

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_icon("icons/icon.png")
        """
        return self.execute_command("set_tray_icon", {"tray_icon_path": tray_icon_path})
    
    def set_tray_menu_items(self, tray_menu_items: List[Dict[str, Union[str, Callable]]]) -> bool:
        """
        Dynamically sets the tray menu items.

        Parameters
        ----------
        tray_menu_items : List[Dict[str, Union[str, Callable]]]
            The list of new tray menu items

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> menu_items = [{"label": "Open", "callback": lambda: print("Open clicked")},
        >>>               {"label": "Exit", "callback": app.quit}]
        >>> app.set_tray_menu_items(menu_items)
        """
        return self.execute_command("set_tray_menu_items", {"tray_menu_items": tray_menu_items})
    
    def set_tray_actions(self, actions: Dict[TrayEvent, Callable]) -> bool:
        """
        Dynamically sets the actions for tray icon activation.

        Parameters
        ----------
        actions : Dict[TrayEvent, Callable]
            Dictionary with TrayEvent enum values as keys and corresponding callback functions as values

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_actions({TrayEvent.DoubleClick: lambda: print("Double-clicked")})
        """
        return self.execute_command("set_tray_actions", {"actions": actions})
    
    def show_notification(self, title: str, message: str) -> bool:
        """
        Displays a notification in the system tray.

        Parameters
        ----------
        title : str
            Notification title
        message : str
            Notification message

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.show_notification("Update Available", "A new update is available for download.")
        """
        return self.execute_command("show_notification", {"title": title, "message": message})
    
    def set_tray_icon_animation(self, icon_frames: List[str], interval: int = 200) -> bool:
        """
        Dynamically sets and starts the animation for the tray icon.

        Parameters
        ----------
        icon_frames : list of str
            List of animation frame image paths
        interval : int, optional
            Frame interval in milliseconds, default is 200

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_icon_animation(["frame1.png", "frame2.png", "frame3.png"], 100)
        """
        return self.execute_command("set_tray_icon_animation", {"icon_frames": icon_frames, "interval": interval})
    
    def set_tray_tooltip(self, message: str) -> bool:
        """
        Dynamically sets the tooltip for the tray icon.

        Parameters
        ----------
        message : str
            New tooltip message

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_tray_tooltip("Pyloid is running")
        """
        return self.execute_command("set_tray_tooltip", {"message": message})
    
    def set_notification_callback(self, callback: Callable[[str], None]) -> bool:
        """
        Sets the callback function to be called when a notification is clicked.

        Parameters
        ----------
        callback : function
            Callback function to be called when a notification is clicked

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> def on_notification_click():
        >>>     print("Notification clicked")
        >>> app.set_notification_callback(on_notification_click)
        """
        return self.execute_command("set_notification_callback", {"callback": callback})
    
    def get_all_monitors(self) -> List[Monitor]:
        """
        Returns information about all connected monitors.

        Returns
        -------
        List[Monitor]
            List containing monitor information

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> monitors = app.get_all_monitors()
        >>> for monitor in monitors:
        >>>     print(monitor.info())
        """
        return self.execute_command("get_all_monitors", {})
    
    def get_primary_monitor(self) -> Monitor:
        """
        Returns information about the primary monitor.

        Returns
        -------
        Monitor
            Primary monitor information

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> primary_monitor = app.get_primary_monitor()
        >>> print(primary_monitor.info())
        """
        return self.execute_command("get_primary_monitor", {})
    
    def set_clipboard_text(self, text: str) -> None:
        """
        Copies text to the clipboard.

        Parameters
        ----------
        text : str
            Text to copy to the clipboard

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_clipboard_text("Hello, World!")
        """
        return self.execute_command("set_clipboard_text", {"text": text})
    
    def get_clipboard_text(self) -> str:
        """
        Retrieves text from the clipboard.

        Returns
        -------
        str
            Text stored in the clipboard

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> text = app.get_clipboard_text()
        >>> print(text)
        """
        return self.execute_command("get_clipboard_text", {})
    
    def set_clipboard_image(self, image: Union[str, bytes, os.PathLike]) -> None:
        """
        Copies an image to the clipboard.

        Parameters
        ----------
        image : Union[str, bytes, os.PathLike]
            Path to the image file to copy to the clipboard

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_clipboard_image("/path/to/image.png")
        """
        return self.execute_command("set_clipboard_image", {"image": image})
    
    def get_clipboard_image(self) -> QImage:
        """
        Retrieves an image from the clipboard.

        Returns
        -------
        QImage
            QImage object stored in the clipboard (None if no image)

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> image = app.get_clipboard_image()
        >>> if image is not None:
        >>>     image.save("/path/to/save/image.png")
        """
        return self.execute_command("get_clipboard_image", {})
    
    def set_auto_start(self, enable: bool) -> Union[bool, None]:
        """
        Sets the application to start automatically at system startup.

        Parameters
        ----------
        enable : bool
            True to enable auto start, False to disable

        Returns
        -------
        bool or None
            True if auto start is successfully set, False if disabled, None if not supported in non-production environment

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_auto_start(True)
        """
        return self.execute_command("set_auto_start", {"enable": enable})
    
    def is_auto_start(self) -> bool:
        """
        Checks if the application is set to start automatically at system startup.

        Returns
        -------
        bool
            True if auto start is enabled, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> auto_start_enabled = app.is_auto_start()
        >>> print(auto_start_enabled)
        """
        return self.execute_command("is_auto_start", {})
    
    def watch_file(self, file_path: str) -> bool:
        """
        Adds a file to the watch list.

        Parameters
        ----------
        file_path : str
            Path to the file to watch

        Returns
        -------
        bool
            True if the file is successfully added to the watch list, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.watch_file("/path/to/file.txt")
        """
        return self.execute_command("watch_file", {"file_path": file_path})
    
    def watch_directory(self, dir_path: str) -> bool:
        """
        Adds a directory to the watch list.

        Parameters
        ----------
        dir_path : str
            Path to the directory to watch

        Returns
        -------
        bool
            True if the directory is successfully added to the watch list, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.watch_directory("/path/to/directory")
        """
        return self.execute_command("watch_directory", {"dir_path": dir_path})
    
    def stop_watching(self, path: str) -> bool:
        """
        Removes a file or directory from the watch list.

        Parameters
        ----------
        path : str
            Path to the file or directory to stop watching

        Returns
        -------
        bool
            True if the path is successfully removed from the watch list, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.stop_watching("/path/to/file_or_directory")
        """
        return self.execute_command("stop_watching", {"path": path})
    
    def get_watched_paths(self) -> List[str]:
        """
        Returns all currently watched paths.

        Returns
        -------
        List[str]
            List of all watched paths

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.get_watched_paths()
        ['/path/to/file1.txt', '/path/to/directory']
        """
        return self.execute_command("get_watched_paths", {})
    
    def get_watched_files(self) -> List[str]:
        """
        Returns all currently watched files.

        Returns
        -------
        List[str]
            List of all watched files

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.get_watched_files()
        ['/path/to/file1.txt', '/path/to/file2.txt']
        """
        return self.execute_command("get_watched_files", {})
    
    def get_watched_directories(self) -> List[str]:
        """
        Returns all currently watched directories.

        Returns
        -------
        List[str]
            List of all watched directories

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.get_watched_directories()
        ['/path/to/directory1', '/path/to/directory2']
        """
        return self.execute_command("get_watched_directories", {})
    
    def remove_all_watched_paths(self) -> None:
        """
        Removes all paths from the watch list.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.remove_all_watched_paths()
        """
        return self.execute_command("remove_all_watched_paths", {})
    
    def set_file_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to be called when a file is changed.

        Parameters
        ----------
        callback : Callable[[str], None]
            Function to be called when a file is changed

        Examples
        --------
        >>> def on_file_change(file_path):
        >>>     print(f"File changed: {file_path}")
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_file_change_callback(on_file_change)
        """
        return self.execute_command("set_file_change_callback", {"callback": callback})
    
    def set_directory_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the callback function to be called when a directory is changed.

        Parameters
        ----------
        callback : Callable[[str], None]
            Function to be called when a directory is changed

        Examples
        --------
        >>> def on_directory_change(dir_path):
        >>>     print(f"Directory changed: {dir_path}")
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> app.set_directory_change_callback(on_directory_change)
        """
        return self.execute_command("set_directory_change_callback", {"callback": callback})
    
    def open_file_dialog(self, dir: Optional[str] = None, filter: Optional[str] = None) -> Optional[str]:
        """
        Opens a file dialog to select a file to open.

        Parameters
        ----------
        dir : str, optional
            The initial directory that the dialog will open in.
        filter : str, optional
            A string that specifies the file types that can be selected.

        Returns
        -------
        Optional[str]
            The path of the selected file or None if no file is selected.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> file_path = app.open_file_dialog(dir="/home/user", filter="Text Files (*.txt)")
        """
        return self.execute_command("open_file_dialog", {"dir": dir, "filter": filter})
    
    def save_file_dialog(self, dir: Optional[str] = None, filter: Optional[str] = None) -> Optional[str]:
        """
        Opens a file dialog to select a file to save.

        Parameters
        ----------
        dir : str, optional
            The initial directory that the dialog will open in.
        filter : str, optional
            A string that specifies the file types that can be saved.

        Returns
        -------
        Optional[str]
            The path of the selected file or None if no file is selected.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> file_path = app.save_file_dialog(dir="/home/user", filter="Text Files (*.txt)")
        """
        return self.execute_command("save_file_dialog", {"dir": dir, "filter": filter})
    
    def select_directory_dialog(self, dir: Optional[str] = None) -> Optional[str]:
        """
        Opens a dialog to select a directory.

        Parameters
        ----------
        dir : str, optional
            The initial directory that the dialog will open in.

        Returns
        -------
        Optional[str]
            The path of the selected directory or None if no directory is selected.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> directory_path = app.select_directory_dialog(dir="/home/user")
        """
        return self.execute_command("select_directory_dialog", {"dir": dir})