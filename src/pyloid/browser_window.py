import sys
import os
from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
    QCursor,
)
from PySide6.QtCore import Qt, QPoint, QUrl, QEvent
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from .api import PyloidAPI
import uuid
from typing import List, Optional, Dict, Callable
import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from .custom.titlebar import CustomTitleBar
from .js_api.window_api import WindowAPI



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
        """
        Loads a local HTML file into the web view.

        Parameters
        ----------
        file_path : str
            The path to the local HTML file to be loaded.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.load_file('/path/to/local/file.html')
        >>> window.show()
        """
        self._load()
        file_path = os.path.abspath(file_path)  # absolute path
        self.web_view.setUrl(QUrl.fromLocalFile(file_path))
        self.web_view.focusProxy().installEventFilter(self.web_view)

    def load_url(self, url):
        """
        Sets the URL of the window.

        Parameters
        ----------
        url : str
            The URL to be loaded in the web view.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.load_url('https://www.example.com')
        >>> window.show()
        """
        self._load()
        self.web_view.setUrl(QUrl(url))
        self.web_view.focusProxy().installEventFilter(self.web_view)

    ###########################################################################################
    # Set Parameters
    ###########################################################################################
    def set_title(self, title: str):
        """
        Sets the title of the window.

        Parameters
        ----------
        title : str
            The title to be set for the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_title('My Window Title')
        """
        self.title = title
        self._window.setWindowTitle(self.title)

    def set_size(self, width: int, height: int):
        """
        Sets the size of the window.

        Parameters
        ----------
        width : int
            The width of the window.
        height : int
            The height of the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_size(800, 600)
        """
        self.width = width
        self.height = height
        self._window.setGeometry(self.x, self.y, self.width, self.height)

    def set_position(self, x: int, y: int):
        """
        Sets the position of the window.

        Parameters
        ----------
        x : int
            The x-coordinate of the window's position.
        y : int
            The y-coordinate of the window's position.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_position(100, 100)
        """
        self.x = x
        self.y = y
        self._window.setGeometry(self.x, self.y, self.width, self.height)

    def set_frame(self, frame: bool):
        """
        Sets the frame of the window.

        Parameters
        ----------
        frame : bool
            If True, the window will have a frame. If False, the window will be frameless.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_frame(True)
        >>> window.set_frame(False)
        """
        self.frame = frame
        was_visible = self._window.isVisible()
        if self.frame:
            self._window.setWindowFlags(Qt.Window)
        else:
            self._window.setWindowFlags(Qt.FramelessWindowHint)
        if was_visible:
            self._window.show()

    def set_context_menu(self, context_menu: bool):
        """
        Sets the context menu of the window.

        Parameters
        ----------
        context_menu : bool
            If True, the context menu will be disabled. If False, the default context menu will be enabled.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_context_menu(True)
        >>> window.set_context_menu(False)
        """
        self.context_menu = context_menu
        if self.context_menu:
            self.web_view.setContextMenuPolicy(Qt.NoContextMenu)
        else:
            self.web_view.setContextMenuPolicy(Qt.DefaultContextMenu)

    def set_dev_tools(self, enable: bool):
        """
        Sets the developer tools of the window.

        If enabled, the developer tools can be opened using the F12 key.

        Parameters
        ----------
        enable : bool
            If True, the developer tools will be enabled. If False, the developer tools will be disabled.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_dev_tools(True)
        >>> window.set_dev_tools(False)
        """
        self.dev_tools = enable
        if self.dev_tools:
            self.add_shortcut("F12", self.open_dev_tools)
        else:
            self.remove_shortcut("F12")

    def open_dev_tools(self):
        """
        Opens the developer tools window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.open_dev_tools()
        """
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
        """
        Hides the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.hide()
        """
        self._window.hide()

    def show(self):
        """
        Shows the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.show()
        """
        self._window.show()

    def focus(self):
        """
        Focuses the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.focus()
        """
        self._window.activateWindow()
        self._window.raise_()
        self._window.setWindowState(
            self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )

    def show_and_focus(self):
        """
        Shows and focuses the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.show_and_focus()
        """
        self._window.show()
        self._window.activateWindow()
        self._window.raise_()
        self._window.setWindowState(
            self._window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )

    def close(self):
        """
        Closes the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.close()
        """
        self._window.close()

    def toggle_fullscreen(self):
        """
        Toggles the fullscreen mode of the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.toggle_fullscreen()
        """
        if self._window.isFullScreen():
            self._window.showNormal()
        else:
            self._window.showFullScreen()

    def minimize(self):
        """
        Minimizes the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.minimize()
        """
        self._window.showMinimized()

    def maximize(self):
        """
        Maximizes the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.maximize()
        """
        self._window.showMaximized()

    def unmaximize(self):
        """
        Restores the window from maximized state.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.unmaximize()
        """
        self._window.showNormal()

    def capture(self, save_path: str) -> Optional[str]:
        """
        Captures the current window.

        Parameters
        ----------
        save_path : str
            Path to save the captured image. If not specified, it will be saved in the current directory.

        Returns
        -------
        Optional[str]
            Returns the path of the saved image.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> save_path = window.capture("screenshot.png")
        >>> print(f"Image saved at: {save_path}")
        Image saved at: screenshot.png
        """
        try:
            # Capture the window
            screenshot = self._window.grab()

            # Save the image
            screenshot.save(save_path)
            return save_path
        except Exception as e:
            print(f"An error occurred while capturing the window: {e}")
            return None

    ###########################################################################################
    # Shortcut
    ###########################################################################################
    def add_shortcut(self, key_sequence: str, callback: Callable):
        """
        Adds a keyboard shortcut to the window if it does not already exist.

        Parameters
        ----------
        key_sequence : str
            Shortcut sequence (e.g., "Ctrl+C")
        callback : Callable
            Function to be executed when the shortcut is pressed

        Returns
        -------
        QShortcut or None
            Created QShortcut object or None if the shortcut already exists

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")

        def on_shortcut():
            print("Shortcut activated!")
        window.add_shortcut("Ctrl+C", on_shortcut)

        app.run()
        ```
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

        Parameters
        ----------
        key_sequence : str
            Shortcut sequence to be removed

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        window.remove_shortcut("Ctrl+C")

        app.run()
        ```
        """
        if key_sequence in self.shortcuts:
            shortcut = self.shortcuts.pop(key_sequence)
            shortcut.setEnabled(False)
            shortcut.deleteLater()

    def get_all_shortcuts(self):
        """
        Returns all registered shortcuts in the window.

        Returns
        -------
        dict
            Dictionary of shortcut sequences and QShortcut objects

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        shortcuts = window.get_all_shortcuts()
        print(shortcuts)

        app.run()
        ```
        """
        return self.shortcuts

    ###########################################################################################
    # Event (Calling the JS from Python)
    ###########################################################################################
    def emit(self, event_name, data: Optional[Dict] = None):
        """
        Emits an event to the JavaScript side.

        Parameters
        ----------
        event_name : str
            Name of the event
        data : dict, optional
            Data to be sent with the event (default is None)

        Examples
        --------
        (Python)
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        window.emit("customEvent", {"message": "Hello, Pyloid!"})

        app.run()
        ```
        ---

        (JavaScript)
        ```javascript
        document.addEventListener('customEvent', (data) => {
            console.log(data.message);
        });
        ```
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
        """
        Returns the properties of the window.

        Returns
        -------
        dict
            Dictionary containing the properties of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        properties = window.get_window_properties()
        print(properties)

        app.run()
        ```
        """
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
        """
        Returns the ID of the window.

        Returns
        -------
        str
            ID of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        window_id = window.get_id()
        print(window_id)

        app.run()
        ```
        """
        return self.id

    def get_size(self) -> Dict[str, int]:
        """
        Returns the size of the window.

        Returns
        -------
        dict
            Dictionary containing the width and height of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        size = window.get_size()
        print(size)

        app.run()
        ```
        """
        return {"width": self.width, "height": self.height}

    def get_position(self) -> Dict[str, int]:
        """
        Returns the position of the window.

        Returns
        -------
        dict
            Dictionary containing the x and y coordinates of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        position = window.get_position()
        print(position)

        app.run()
        ```
        """
        return {"x": self.x, "y": self.y}

    def get_title(self) -> str:
        """
        Returns the title of the window.

        Returns
        -------
        str
            Title of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        title = window.get_title()
        print(title)

        app.run()
        ```
        """
        return self.title

    def get_url(self) -> str:
        """
        Returns the URL of the window.

        Returns
        -------
        str
            URL of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        url = window.get_url()
        print(url)

        app.run()
        ```
        """
        return self.web_view.url().toString()

    def get_visible(self) -> bool:
        """
        Returns the visibility of the window.

        Returns
        -------
        bool
            True if the window is visible, False otherwise

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        visible = window.get_visible()
        print(visible)

        app.run()
        ```
        """
        return self._window.isVisible()
    
    def get_frame(self) -> bool:
        """
        Returns the frame enabled state of the window.

        Returns
        -------
        bool
            True if the frame is enabled, False otherwise

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        frame = window.get_frame()
        print(frame)

        app.run()
        ```
        """
        return self.frame
    
    ###########################################################################################
    # Resize
    ###########################################################################################
    def set_resizable(self, resizable: bool):
        """
        Sets the resizability of the window.

        Parameters
        ----------
        resizable : bool
            True to make the window resizable, False to make it fixed size

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        window.set_resizable(True)

        app.run()
        ```
        """
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
        """
        Sets the minimum size of the window.

        Parameters
        ----------
        min_width : int
            Minimum width of the window
        min_height : int
            Minimum height of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        window.set_minimum_size(400, 300)

        app.run()
        ```
        """
        self._window.setMinimumSize(min_width, min_height)

    def set_maximum_size(self, max_width: int, max_height: int):
        """
        Sets the maximum size of the window.

        Parameters
        ----------
        max_width : int
            Maximum width of the window
        max_height : int
            Maximum height of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        window.set_maximum_size(1024, 768)

        app.run()
        ```
        """
        self._window.setMaximumSize(max_width, max_height)

    def get_minimum_size(self) -> Dict[str, int]:
        """
        Returns the minimum size of the window.

        Returns
        -------
        dict
            Dictionary containing the minimum width and height of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        min_size = window.get_minimum_size()
        print(min_size)

        app.run()
        ```
        """
        return {'width': self._window.minimumWidth(), 'height': self._window.minimumHeight()}

    def get_maximum_size(self) -> Dict[str, int]:
        """
        Returns the maximum size of the window.

        Returns
        -------
        dict
            Dictionary containing the maximum width and height of the window

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        max_size = window.get_maximum_size()
        print(max_size)

        app.run()
        ```
        """
        return {'width': self._window.maximumWidth(), 'height': self._window.maximumHeight()}
    
    def get_resizable(self) -> bool:
        """
        Returns the resizability of the window.

        Returns
        -------
        bool
            True if the window is resizable, False otherwise

        Examples
        --------
        ```python
        app = Pyloid(app_name="Pyloid-App")

        window = app.create_window("pyloid-window")
        resizable = window.get_resizable()
        print(resizable)

        app.run()
        ```
        """
        return self.resizable