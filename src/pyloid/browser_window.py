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
)
from PySide6.QtCore import Qt, QPoint, QUrl, QEvent, QFile, QEventLoop, QTimer, QObject, Signal, Slot
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineSettings,
)
from .api import PyloidAPI
import uuid
from typing import List, Optional, Dict, Callable
import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from .custom.titlebar import CustomTitleBar
from .js_api.base import BaseAPI
from PySide6.QtGui import QPixmap, QMovie
from PySide6.QtWidgets import QSplashScreen, QLabel
from typing import TYPE_CHECKING, Any
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineDesktopMediaRequest

if TYPE_CHECKING:
    from .pyloid import _Pyloid


class CustomWebPage(QWebEnginePage):
    def __init__(self, profile=None):
        super().__init__(profile)
        self.featurePermissionRequested.connect(self._handlePermissionRequest)
        self.desktopMediaRequested.connect(self._handleDesktopMediaRequest)
        self._permission_handlers = {}
        self._desktop_media_handler = None
        self._url_handlers = {}  # URL 핸들러 저장을 위한 딕셔너리 추가

        # interceptor ( all url request )
        # self.interceptor = CustomUrlInterceptor()
        # self.profile().setUrlRequestInterceptor(self.interceptor)

    def _handlePermissionRequest(self, origin: QUrl, feature: QWebEnginePage.Feature):
        # print(origin, feature)

        """Default permission request handler"""
        if feature in self._permission_handlers:
            # Execute if a handler is registered
            handler = self._permission_handlers[feature]
            handler(origin, feature)
        else:
            # Allow all permissions by default
            self.setFeaturePermission(
                origin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )

    def setPermissionHandler(self, feature: QWebEnginePage.Feature, handler):
        """Register a handler for a specific permission"""
        self._permission_handlers[feature] = handler

    def _handleDesktopMediaRequest(self, request: QWebEngineDesktopMediaRequest):
        return
        print("Desktop media request received:", request)

        # 사용 가능한 화면 목록 확인
        screens_model = request.screensModel()
        print("\n=== Available Screens ===")
        for i in range(screens_model.rowCount()):
            screen_index = screens_model.index(i)
            screen_name = screens_model.data(screen_index)
            print(f"Screen {i}: {screen_name}")

        # 사용 가능한 창 목록 확인
        windows_model = request.windowsModel()
        print("\n=== Available Windows ===")
        for i in range(windows_model.rowCount()):
            window_index = windows_model.index(i)
            window_name = windows_model.data(window_index)
            print(f"Window {i}: {window_name}")
            
        request.selectWindow(windows_model.index(3))

    # # interceptor ( navigation request )
    # def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
    #     """네비게이션 요청을 처리하는 메서드"""
    #     print(f"Navigation Request - URL: {url.toString()}")
    #     print(f"Navigation Type: {navigation_type}")
    #     print(f"Is Main Frame: {is_main_frame}")

    #     return True


# interceptor ( all url request )
# class CustomUrlInterceptor(QWebEngineUrlRequestInterceptor):
#     def interceptRequest(self, info):
#         url = info.requestUrl().toString()
#         print(url)

# class CustomInterceptor(QWebEngineUrlRequestInterceptor):
#     def __init__(self, index_path=None):
#         super().__init__()
#         self.index_path = get_production_path()
#         self.last_path = "/"
        
#     def interceptRequest(self, info):
#         url = info.requestUrl()
#         navigation_type = info.navigationType()

#         print("--------------------------------")
        
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeTyped:
#             print("NavigationTypeTyped")
            
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeReload:
#             print("NavigationTypeReload")
            
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeBackForward:
#             print("NavigationTypeBackForward")
        
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
#             print("NavigationTypeLinkClicked")
            
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeFormSubmitted:
#             print("NavigationTypeFormSubmitted")
            
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeTyped:
#             print("NavigationTypeTyped")
            
#         if navigation_type == QWebEnginePage.NavigationType.NavigationTypeOther:
#             print("NavigationTypeOther")
            
#         print(navigation_type.value)
        
#         print(url)
#         print(url.scheme())
#         print(url.host())
#         print(url.url())
#         print(self.last_path)
        
#         self.last_path = url.path()


class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent: "BrowserWindow" = None):
        super().__init__(parent._window)
        self.parent: "BrowserWindow" = parent

        # Custom Web Page
        self.custom_page = CustomWebPage()
        self.setPage(self.custom_page)

        self.is_resizing = False
        self.resize_start_pos = None
        self.resize_direction = None
        self.screen_geometry = self.screen().virtualGeometry()
        self.is_resizing_enabled = True

        self.setAttribute(Qt.WA_SetCursor, False)

        self.is_in_resize_area = False

    def mouse_press_event(self, event):
        if self.parent.frame or not self.is_resizing_enabled:
            return

        if event.button() == Qt.LeftButton:
            self.resize_direction = self.get_resize_direction(event.pos())
            if self.resize_direction:
                self.is_resizing = True
                self.resize_start_pos = event.globalPos()

    def start_system_drag(self):
        """Start system window move"""
        if self.parent._window.windowHandle():
            self.parent._window.windowHandle().startSystemMove()

    def mouse_move_event(self, event):
        if self.parent.frame or not self.is_resizing_enabled:
            return

        # Check resize direction
        was_in_resize_area = self.is_in_resize_area
        resize_direction = self.get_resize_direction(event.pos())
        self.is_in_resize_area = bool(resize_direction)

        if resize_direction and not self.is_resizing:
            self.set_cursor_for_resize_direction(resize_direction)

        if self.is_resizing:
            self.resize_window(event.globalPos())
            return

        # Change cursor when entering/leaving resize area
        if self.is_in_resize_area != was_in_resize_area:
            if self.is_in_resize_area:
                # self.setAttribute(Qt.WA_SetCursor, True)
                pass
            else:
                self.unsetCursor()
                # self.setAttribute(Qt.WA_SetCursor, False)

    def mouse_release_event(self, event):
        if self.parent.frame or not self.is_resizing_enabled:
            return

        if event.button() == Qt.LeftButton:
            self.is_resizing = False

            if self.resize_direction:
                self.unsetCursor()
                self.resize_direction = None

            self.setAttribute(Qt.WA_SetCursor, False)

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
        if (
            not self.parent.frame and self.is_resizing_enabled
        ):  # Check if frame is not present and resizing is enabled
            margin = 8  # Margin in pixels to detect edge
            rect = self.rect()
            direction = None

            if pos.x() <= margin:
                direction = "left"
            elif pos.x() >= rect.width() - margin:
                direction = "right"

            if pos.y() <= margin:
                direction = "top" if direction is None else direction + "-top"
            elif pos.y() >= rect.height() - margin:
                direction = "bottom" if direction is None else direction + "-bottom"

            return direction
        return None

    def set_cursor_for_resize_direction(self, direction):
        if not self.parent.frame and direction and self.is_resizing_enabled:
            cursor = None
            if direction in ["left", "right"]:
                cursor = Qt.SizeHorCursor
            elif direction in ["top", "bottom"]:
                cursor = Qt.SizeVerCursor
            elif direction in ["left-top", "right-bottom"]:
                cursor = Qt.SizeFDiagCursor
            elif direction in ["right-top", "left-bottom"]:
                cursor = Qt.SizeBDiagCursor

            if cursor:
                self.setCursor(cursor)
                self.setAttribute(Qt.WA_SetCursor, True)

    def resize_window(self, global_pos):
        if (
            not self.parent.frame
            and self.resize_start_pos
            and self.resize_direction
            and self.is_resizing_enabled
        ):  # Check if frame is not present and resizing is enabled
            delta = global_pos - self.resize_start_pos
            new_geometry = self.parent._window.geometry()

            if "left" in self.resize_direction:
                new_geometry.setLeft(new_geometry.left() + delta.x())
            if "right" in self.resize_direction:
                new_geometry.setRight(new_geometry.right() + delta.x())
            if "top" in self.resize_direction:
                new_geometry.setTop(new_geometry.top() + delta.y())
            if "bottom" in self.resize_direction:
                new_geometry.setBottom(new_geometry.bottom() + delta.y())

            self.parent._window.setGeometry(new_geometry)
            self.resize_start_pos = global_pos


class _BrowserWindow:
    def __init__(
        self,
        app: "_Pyloid",
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
        self.js_apis = [BaseAPI(self.id, self.app.data)]
        for js_api in js_apis:
            self.js_apis.append(js_api)
        self.shortcuts = {}
        self.close_on_load = True
        self.splash_screen = None
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

        # allow local file access to remote urls and screen capture
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AutoLoadImages, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ErrorPageEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ShowScrollBars, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.PdfViewerEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True
        )
        self.web_view.settings().setUnknownUrlSchemePolicy(
            QWebEngineSettings.UnknownUrlSchemePolicy.AllowAllUnknownUrlSchemes
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanPaste, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, False
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
                # Define window_id, window, and app for each JS API
                js_api.window_id = self.id
                js_api.window = self
                js_api.app = self.app

                self.channel.registerObject(js_api.__class__.__name__, js_api)

        self.web_view.page().setWebChannel(self.channel)

        # Connect pylonjs bridge
        self.web_view.loadFinished.connect(self._on_load_finished)

        # Add QWebEngineView to main window
        self._window.setCentralWidget(self.web_view)

        # Set F12 shortcut
        self.set_dev_tools(self.dev_tools)
        
        # 프로필 가져오기 및 인터셉터 설정
        profile = self.web_view.page().profile()
        
        # # 기존 인터셉터가 있다면 제거
        # if self.interceptor:
        #     profile.setUrlRequestInterceptor(None)

    def _on_load_finished(self, ok):
        """Handles the event when the web page finishes loading."""
        if ok and self.js_apis:
            # Load qwebchannel.js
            qwebchannel_js = QFile("://qtwebchannel/qwebchannel.js")
            if qwebchannel_js.open(QFile.ReadOnly):
                source = bytes(qwebchannel_js.readAll()).decode("utf-8")
                self.web_view.page().runJavaScript(source)
                qwebchannel_js.close()

            js_code = """
            if (typeof QWebChannel !== 'undefined') {
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    window.pyloid = {
                        EventAPI: {
                            _listeners: {},  // 콜백 함수들을 저장할 객체
                            
                            listen: function(eventName, callback) {
                                // 이벤트에 대한 콜백 배열이 없다면 생성
                                if (!this._listeners[eventName]) {
                                    this._listeners[eventName] = [];
                                }
                                
                                // 콜백 함수 저장
                                this._listeners[eventName].push(callback);
                                
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
                                // 해당 이벤트의 모든 리스너 제거
                                if (this._listeners[eventName]) {
                                    this._listeners[eventName].forEach(callback => {
                                        document.removeEventListener(eventName, callback);
                                    });
                                    // 저장된 콜백 제거
                                    delete this._listeners[eventName];
                                }
                            }
                        }   
                    };
                    console.log('pyloid.EventAPI object initialized:', window.pyloid.EventAPI);

                    %s
                    
                    document.addEventListener('mousedown', function (e) {
                        if (e.target.hasAttribute('data-pyloid-drag-region')) {
                            window.pyloid.BaseAPI.startSystemDrag();
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
            self.web_view.page().runJavaScript(js_code % (js_api_init))

            # if splash screen is set, close it when the page is loaded
            if self.close_on_load and self.splash_screen:
                self.close_splash_screen()
        else:
            pass

    ###########################################################################################
    # Load
    ###########################################################################################
    def load_file(self, file_path: str):
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

    def load_url(self, url: str):
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

    def load_html(self, html_content: str, base_url: str = ""):
        """
        Loads HTML content directly into the web view.

        Parameters
        ----------
        html_content : str
            The HTML content to be loaded.
        base_url : str, optional
            The base URL to use for resolving relative URLs (default is "").

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> html_content = "<html><body><h1>Hello, Pyloid!</h1></body></html>"
        >>> window.load_html(html_content)
        >>> window.show()
        """
        self._load()
        self.web_view.setHtml(html_content, QUrl(base_url))
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

    def set_position_by_anchor(self, anchor: str):
        """
        Positions the window at a specific location on the screen.

        Parameters
        ----------
        anchor : str
            The anchor point indicating where to position the window.
            Possible values: 'center', 'top', 'bottom', 'left', 'right',
                             'top-left', 'top-right', 'bottom-left', 'bottom-right'

        Examples
        --------
        >>> window.set_position_by_anchor('center')
        >>> window.set_position_by_anchor('top-right')
        """
        screen = self.app.primaryScreen().availableGeometry()
        window_size = self.get_size()

        if anchor == "center":
            x = (screen.width() - window_size["width"]) // 2
            y = (screen.height() - window_size["height"]) // 2
        elif anchor == "top":
            x = (screen.width() - window_size["width"]) // 2
            y = screen.top()
        elif anchor == "bottom":
            x = (screen.width() - window_size["width"]) // 2
            y = screen.bottom() - window_size["height"]
        elif anchor == "left":
            x = screen.left()
            y = (screen.height() - window_size["height"]) // 2
        elif anchor == "right":
            x = screen.right() - window_size["width"]
            y = (screen.height() - window_size["height"]) // 2
        elif anchor == "top-left":
            x = screen.left()
            y = screen.top()
        elif anchor == "top-right":
            x = screen.right() - window_size["width"]
            y = screen.top()
        elif anchor == "bottom-left":
            x = screen.left()
            y = screen.bottom() - window_size["height"]
        elif anchor == "bottom-right":
            x = screen.right() - window_size["width"]
            y = screen.bottom() - window_size["height"]
        else:
            raise ValueError("Invalid anchor point.")

        self.set_position(x, y)

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
        if self in self.app.windows_dict:
            self.app.windows_dict.pop(self.id)
        if not self.app.windows_dict:
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
        was_on_top = bool(self._window.windowFlags() & Qt.WindowStaysOnTopHint)
        if not was_on_top:
            self._window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self._window.show()
        self._window.activateWindow()
        if not was_on_top:
            self._window.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self._window.show()

    def show_and_focus(self):
        """
        Shows and focuses the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.show_and_focus()
        """
        was_on_top = bool(self._window.windowFlags() & Qt.WindowStaysOnTopHint)
        if not was_on_top:
            self._window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self._window.show()
        self._window.activateWindow()
        if not was_on_top:
            self._window.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self._window.show()

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

    def fullscreen(self):
        """
        Enters fullscreen mode.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.fullscreen()
        """
        self._window.showFullScreen()

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

    def toggle_maximize(self):
        """
        Toggles the maximized state of the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.toggle_maximize()
        """
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def is_fullscreen(self) -> bool:
        """
        Returns True if the window is fullscreen.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.is_fullscreen()
        """
        return self._window.isFullScreen()

    def is_maximized(self) -> bool:
        """
        Returns True if the window is maximized.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.is_maximized()
        """
        return self._window.isMaximized()

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
    def invoke(self, event_name, data: Optional[Dict] = None):
        """
        Invokes an event to the JavaScript side.

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
        window.invoke("customEvent", {"message": "Hello, Pyloid!"})

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
        return {
            "width": self._window.minimumWidth(),
            "height": self._window.minimumHeight(),
        }

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
        return {
            "width": self._window.maximumWidth(),
            "height": self._window.maximumHeight(),
        }

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

    ###########################################################################################
    # For Custom Pyside6 Features
    ###########################################################################################
    # def get_QMainWindow(self) -> QMainWindow:
    #     """
    #     Returns the QMainWindow object of the window.

    #     you can use all the features of QMainWindow for customizing the window.

    #     Returns
    #     -------
    #     QMainWindow
    #         QMainWindow object of the window

    #     Examples
    #     --------
    #     ```python
    #     from PySide6.QtCore import Qt
    #     from pyloid import Pyloid

    #     app = Pyloid(app_name="Pyloid-App")

    #     window = app.create_window("pyloid-window")
    #     qmain = window.get_QMainWindow()

    #     qmain.setWindowFlags(qmain.windowFlags() | Qt.WindowStaysOnTopHint) # window stays on top
    #     ```
    #     """
    #     return self._window

    # def get_QWebEngineView(self) -> CustomWebEngineView:
    #     """
    #     Returns the CustomWebEngineView object which inherits from QWebEngineView.

    #     Returns
    #     -------
    #     CustomWebEngineView
    #         CustomWebEngineView object of the window

    #     Examples
    #     --------
    #     ```python
    #     window = app.create_window("pyloid-window")
    #     web_view = window.get_QWebEngineView()

    #     web_view.page().runJavaScript("console.log('Hello, Pyloid!')")
    #     ```
    #     """
    #     return self.web_view

    ###########################################################################################
    # QMainWindow flags
    ###########################################################################################
    def set_window_stay_on_top(self, on_top: bool):
        """
        Sets the window stay on top flag of the window.

        Parameters
        ----------
        on_top : bool
            True to keep the window on top, False otherwise

        Examples
        --------
        ```python
        window.set_window_stay_on_top(True)
        window.set_window_stay_on_top(False)
        ```
        """
        flags = self._window.windowFlags()
        if on_top:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint

        # Maintain existing flags while only changing WindowStaysOnTopHint
        # Explicitly add the close button
        flags |= Qt.WindowCloseButtonHint

        self._window.setWindowFlags(flags)

        # Show the window again to apply the changes
        self._window.show()

    def set_window_stay_on_bottom(self, on_bottom: bool):
        """
        Sets the window stay on bottom flag of the window.

        Parameters
        ----------
        on_bottom : bool
            True to keep the window on bottom, False otherwise

        Examples
        --------
        ```python
        window.set_window_stay_on_bottom(True)
        window.set_window_stay_on_bottom(False)
        ```
        """
        flags = self._window.windowFlags()
        if on_bottom:
            flags |= Qt.WindowStaysOnBottomHint
        else:
            flags &= ~Qt.WindowStaysOnBottomHint

        # Maintain existing flags while only changing WindowStaysOnBottomHint
        # Explicitly add the close button
        flags |= Qt.WindowCloseButtonHint

        self._window.setWindowFlags(flags)

        # Show the window again to apply the changes
        self._window.show()

    ###########################################################################################
    # Splash Screen
    ###########################################################################################
    def set_static_image_splash_screen(
        self,
        image_path: str,
        close_on_load: bool = True,
        stay_on_top: bool = True,
        clickable: bool = True,
        position: str = "center",
    ):
        """
        Sets the static image splash screen of the window.

        Parameters
        ----------
        image_path : str
            Path to the image file
        close_on_load : bool, optional
            True to close the splash screen when the page is loaded, False otherwise (default is True)
        stay_on_top : bool, optional
            True to keep the splash screen on top, False otherwise (default is True)
        clickable : bool, optional
            True to make the splash screen clickable, False otherwise (default is True)
            if clickable is True, you can click the splash screen to close it.
        position : str, optional
            Position of the splash screen. Options are 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right' (default is 'center')

        Examples
        --------
        ```python
        window.set_static_image_splash_screen("./assets/loading.png", close_on_load=True, stay_on_top=True)
        ```
        """
        pixmap = QPixmap(image_path)

        if not clickable:

            class NonClickableSplashScreen(QSplashScreen):
                def mousePressEvent(self, event):
                    pass  # Ignore click events

            splash = NonClickableSplashScreen(
                pixmap, Qt.WindowStaysOnTopHint if stay_on_top else Qt.WindowType(0)
            )
        else:
            splash = QSplashScreen(
                pixmap, Qt.WindowStaysOnTopHint if stay_on_top else Qt.WindowType(0)
            )

        self.close_on_load = close_on_load
        self.splash_screen = splash
        self._position_splash_screen(position)
        self.splash_screen.show()

    def set_gif_splash_screen(
        self,
        gif_path: str,
        close_on_load: bool = True,
        stay_on_top: bool = True,
        clickable: bool = True,
        position: str = "center",
    ):
        """
        Sets the gif splash screen of the window.

        Parameters
        ----------
        gif_path : str
            Path to the gif file
        close_on_load : bool, optional
            True to close the splash screen when the page is loaded, False otherwise (default is True)
        stay_on_top : bool, optional
            True to keep the splash screen on top, False otherwise (default is True)
        clickable : bool, optional
            True to make the splash screen clickable, False otherwise (default is True)
            if clickable is True, you can click the splash screen to close it.
        position : str, optional
            Position of the splash screen. Options are 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right' (default is 'center')

        Examples
        --------
        ```python
        window.set_gif_splash_screen("./assets/loading.gif", close_on_load=True, stay_on_top=True)
        ```
        """

        if not clickable:

            class NonClickableSplashScreen(QSplashScreen):
                def mousePressEvent(self, event):
                    pass  # Ignore click events

            # Create splash screen (using animated GIF)
            splash = NonClickableSplashScreen(
                QPixmap(1, 1),
                Qt.WindowStaysOnTopHint if stay_on_top else Qt.WindowType(0),
            )  # Start with 1x1 transparent pixmap
        else:
            splash = QSplashScreen(
                QPixmap(1, 1),
                Qt.WindowStaysOnTopHint if stay_on_top else Qt.WindowType(0),
            )

        splash.setAttribute(Qt.WA_TranslucentBackground)

        # Create QLabel for GIF animation
        label = QLabel(splash)
        movie = QMovie(gif_path)
        label.setMovie(movie)

        # Adjust splash screen size to match GIF size
        movie.frameChanged.connect(
            lambda: splash.setFixedSize(movie.currentPixmap().size())
        )

        # Start animation and show splash screen
        movie.start()
        self.close_on_load = close_on_load
        self.splash_screen = splash
        self._position_splash_screen(position)
        splash.show()

    def _position_splash_screen(self, position: str):
        if not self.splash_screen:
            return

        screen = self.app.primaryScreen().geometry()
        splash_size = self.splash_screen.size()

        if position == "center":
            new_position = screen.center() - QPoint(
                splash_size.width() // 2, splash_size.height() // 2
            )
        elif position == "top-left":
            new_position = screen.topLeft()
        elif position == "top-right":
            new_position = screen.topRight() - QPoint(splash_size.width(), 0)
        elif position == "bottom-left":
            new_position = screen.bottomLeft() - QPoint(0, splash_size.height())
        elif position == "bottom-right":
            new_position = screen.bottomRight() - QPoint(
                splash_size.width(), splash_size.height()
            )
        else:
            new_position = screen.center() - QPoint(
                splash_size.width() // 2, splash_size.height() // 2
            )

        self.splash_screen.move(new_position)

    def close_splash_screen(self):
        """
        Closes the splash screen if it exists.

        Examples
        --------
        ```python
        window.close_splash_screen()
        ```
        """
        if hasattr(self, "splash_screen") and self.splash_screen:
            self.splash_screen.close()
            self.close_on_load = None
            self.splash_screen = None

    ###########################################################################################
    # WebEngineView Attribute setting
    ###########################################################################################
    # def set_web_engine_view_attribute(self, attribute: QWebEngineSettings, on: bool):
    #     """
    #     Sets the attribute of the WebEngineView.

    #     Parameters
    #     ----------
    #     attribute : QWebEngineSettings
    #         Attribute to set
    #     on : bool
    #         True to enable the attribute, False to disable it

    #     Examples
    #     --------
    #     ```python
    #     window.set_web_engine_view_attribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, False)
    #     ```
    #     """
    #     settings = self.web_view.settings()
    #     settings.setAttribute(attribute, on)

    # def is_web_engine_view_attribute(self, attribute: QWebEngineSettings) -> bool:
    #     """
    #     Returns the attribute of the WebEngineView.

    #     Parameters
    #     ----------
    #     attribute : QWebEngineSettings
    #         Attribute to get

    #     Returns
    #     -------
    #     bool
    #         True if the attribute is enabled, False otherwise

    #     Examples
    #     --------
    #     ```python
    #     window.is_web_engine_view_attribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled)
    #     ```
    #     """
    #     settings = self.web_view.settings()
    #     return settings.testAttribute(attribute)

    # def set_permission_handler(self, feature: QWebEnginePage.Feature, handler):
    #     """
    #     Sets a handler for a specific permission.

    #     Parameters
    #     ----------
    #     feature : QWebEnginePage.Feature
    #         The type of permission to set
    #     handler : callable
    #         The handler function to process the permission request

    #     Examples
    #     --------
    #     ```python
    #     def handle_camera(origin, feature):
    #         window.web_view.page().setFeaturePermission(
    #             origin,
    #             feature,
    #             QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
    #         )

    #     window.set_permission_handler(
    #         QWebEnginePage.Feature.MediaVideoCapture,
    #         handle_camera
    #     )
    #     ```
    #     """
    #     self.web_view.custom_page.setPermissionHandler(feature, handler)

    # def grant_permission(self, feature: QWebEnginePage.Feature):
    #     """
    #     Automatically grants a specific permission when a request is made.

    #     Parameters
    #     ----------
    #     feature : QWebEnginePage.Feature
    #         The type of permission to automatically grant

    #     Examples
    #     --------
    #     ```python
    #     window.grant_permission(QWebEnginePage.Feature.MediaVideoCapture)
    #     ```
    #     """

    #     def auto_grant(origin, feat):
    #         self.web_view.page().setFeaturePermission(
    #             origin, feat, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
    #         )

    #     self.set_permission_handler(feature, auto_grant)

    # def deny_permission(self, feature: QWebEnginePage.Feature):
    #     """
    #     Automatically denies a specific permission when a request is made.

    #     Parameters
    #     ----------
    #     feature : QWebEnginePage.Feature
    #         The type of permission to automatically deny

    #     Examples
    #     --------
    #     ```python
    #     window.deny_permission(QWebEnginePage.Feature.Notifications)
    #     ```
    #     """

    #     def auto_deny(origin, feat):
    #         self.web_view.page().setFeaturePermission(
    #             origin, feat, QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
    #         )

    #     self.set_permission_handler(feature, auto_deny)

    # def set_desktop_media_handler(self, handler):
    #     """
    #     데스크톱 미디어(화면/윈도우) 선택 핸들러를 설정합니다.

    #     Parameters
    #     ----------
    #     handler : callable
    #         요청을 처리할 핸들러 함수. QWebEngineDesktopMediaRequest 인자로 받습니다.

    #     Examples
    #     --------
    #     ```python
    #     def custom_media_handler(request):
    #         # 사용 가능한 화면 목록 출력
    #         for screen in request.screenList():
    #             print(f"Screen: {screen.name}")

    #         # 사용 가능한 윈도우 목록 출력
    #         for window in request.windowList():
    #             print(f"Window: {window.name}")

    #         # 첫 번째 화면 선택
    #         if request.screenList():
    #             request.selectScreen(request.screenList()[0])

    #     window.set_desktop_media_handler(custom_media_handler)
    #     ```
    #     """
    #     self.web_view.custom_page.setDesktopMediaHandler(handler)


# This wrapper class work in other thread
class BrowserWindow(QObject):
    command_signal = Signal(str, str, object)
    result_signal = Signal(str, object)
    
    def __init__(self, app, title: str, width: int, height: int, x: int, y: int, frame: bool, context_menu: bool, dev_tools: bool, js_apis: List[PyloidAPI]):
        super().__init__()
        self._window = _BrowserWindow(app, title, width, height, x, y, frame, context_menu, dev_tools, js_apis)
        self.command_signal.connect(self._handle_command)
    
    @Slot(str, str, object)
    def _handle_command(self, command_id: str, command_type: str, params: object) -> None:
        """
        Handles commands sent from multiple threads.
        Calls the corresponding method of _BrowserWindow based on the command type and returns the result.

        :param command_id: Unique identifier for each command
        :param command_type: Type of command to execute (e.g., "load_file", "set_title", etc.)
        :param params: Object containing parameters needed for command execution
        """
        result = None

        if command_type == "load_file":
            result = self._window.load_file(params["file_path"])
        elif command_type == "load_url":
            result = self._window.load_url(params["url"])
        elif command_type == "load_html":
            html_content = params.get("html_content", "")
            base_url = params.get("base_url", "")
            result = self._window.load_html(html_content, base_url)
        elif command_type == "set_title":
            result = self._window.set_title(params["title"])
        elif command_type == "set_size":
            result = self._window.set_size(params["width"], params["height"])
        elif command_type == "set_position":
            result = self._window.set_position(params["x"], params["y"])
        elif command_type == "set_position_by_anchor":
            result = self._window.set_position_by_anchor(params["anchor"])
        elif command_type == "set_frame":
            result = self._window.set_frame(params["frame"])
        elif command_type == "set_context_menu":
            result = self._window.set_context_menu(params["context_menu"])
        elif command_type == "set_dev_tools":
            result = self._window.set_dev_tools(params["enable"])
        elif command_type == "open_dev_tools":
            result = self._window.open_dev_tools()
        elif command_type == "hide":
            result = self._window.hide()
        elif command_type == "show":
            result = self._window.show()
        elif command_type == "focus":
            result = self._window.focus()
        elif command_type == "show_and_focus":
            result = self._window.show_and_focus()
        elif command_type == "close":
            result = self._window.close()
        elif command_type == "fullscreen":
            result = self._window.fullscreen()
        elif command_type == "toggle_fullscreen":
            result = self._window.toggle_fullscreen()
        elif command_type == "minimize":
            result = self._window.minimize()
        elif command_type == "maximize":
            result = self._window.maximize()
        elif command_type == "unmaximize":
            result = self._window.unmaximize()
        elif command_type == "toggle_maximize":
            result = self._window.toggle_maximize()
        elif command_type == "is_fullscreen":
            result = self._window.is_fullscreen()
        elif command_type == "is_maximized":
            result = self._window.is_maximized()
        elif command_type == "capture":
            result = self._window.capture(params["save_path"])
        elif command_type == "add_shortcut":
            result = self._window.add_shortcut(params["key_sequence"], params["callback"])
        elif command_type == "remove_shortcut":
            result = self._window.remove_shortcut(params["key_sequence"])
        elif command_type == "get_all_shortcuts":
            result = self._window.get_all_shortcuts()
        elif command_type == "emit":
            event_name = params["event_name"]
            data = params.get("data")
            result = self._window.invoke(event_name, data)
        elif command_type == "get_window_properties":
            result = self._window.get_window_properties()
        elif command_type == "get_id":
            result = self._window.get_id()
        elif command_type == "get_size":
            result = self._window.get_size()
        elif command_type == "get_position":
            result = self._window.get_position()
        elif command_type == "get_title":
            result = self._window.get_title()
        elif command_type == "get_url":
            result = self._window.get_url()
        elif command_type == "get_visible":
            result = self._window.get_visible()
        elif command_type == "get_frame":
            result = self._window.get_frame()
        elif command_type == "set_resizable":
            result = self._window.set_resizable(params["resizable"])
        elif command_type == "set_minimum_size":
            result = self._window.set_minimum_size(params["min_width"], params["min_height"])
        elif command_type == "set_maximum_size":
            result = self._window.set_maximum_size(params["max_width"], params["max_height"])
        elif command_type == "get_minimum_size":
            result = self._window.get_minimum_size()
        elif command_type == "get_maximum_size":
            result = self._window.get_maximum_size()
        elif command_type == "get_resizable":
            result = self._window.get_resizable()
        elif command_type == "set_static_image_splash_screen":
            result = self._window.set_static_image_splash_screen(
                params["image_path"],
                params.get("close_on_load", True),
                params.get("stay_on_top", True),
                params.get("clickable", True),
                params.get("position", "center")
            )
        elif command_type == "set_gif_splash_screen":
            result = self._window.set_gif_splash_screen(
                params["gif_path"],
                params.get("close_on_load", True),
                params.get("stay_on_top", True),
                params.get("clickable", True),
                params.get("position", "center")
            )
        elif command_type == "close_splash_screen":
            result = self._window.close_splash_screen()
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
    # Execute_command wrapper functions
    # -------------------------------------------------------------------
    def load_file(self, file_path: str) -> None:
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
        return self.execute_command("load_file", {"file_path": file_path})

    def load_url(self, url: str) -> None:
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
        return self.execute_command("load_url", {"url": url})

    def load_html(self, html_content: str, base_url: str = "") -> None:
        """
        Loads HTML content directly into the web view.

        Parameters
        ----------
        html_content : str
            The HTML content to be loaded.
        base_url : str, optional
            The base URL to use for resolving relative URLs (default is "").

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> html_content = "<html><body><h1>Hello, Pyloid!</h1></body></html>"
        >>> window.load_html(html_content)
        >>> window.show()
        """
        return self.execute_command("load_html", {"html_content": html_content, "base_url": base_url})

    def set_title(self, title: str) -> None:
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
        return self.execute_command("set_title", {"title": title})

    def set_size(self, width: int, height: int) -> None:
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
        return self.execute_command("set_size", {"width": width, "height": height})

    def set_position(self, x: int, y: int) -> None:
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
        return self.execute_command("set_position", {"x": x, "y": y})

    def set_position_by_anchor(self, anchor: str) -> None:
        """
        Positions the window at a specific location on the screen.

        Parameters
        ----------
        anchor : str
            The anchor point indicating where to position the window.
            Possible values: 'center', 'top', 'bottom', 'left', 'right',
                             'top-left', 'top-right', 'bottom-left', 'bottom-right'

        Examples
        --------
        >>> window.set_position_by_anchor('center')
        >>> window.set_position_by_anchor('top-right')
        """
        return self.execute_command("set_position_by_anchor", {"anchor": anchor})

    def set_frame(self, frame: bool) -> None:
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
        return self.execute_command("set_frame", {"frame": frame})

    def set_context_menu(self, context_menu: bool) -> None:
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
        return self.execute_command("set_context_menu", {"context_menu": context_menu})

    def set_dev_tools(self, enable: bool) -> None:
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
        return self.execute_command("set_dev_tools", {"enable": enable})

    def open_dev_tools(self) -> None:
        """
        Opens the developer tools window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.open_dev_tools()
        """
        return self.execute_command("open_dev_tools", {})

    def hide(self) -> None:
        """
        Hides the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.hide()
        """
        return self.execute_command("hide", {})

    def show(self) -> None:
        """
        Shows the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.show()
        """
        return self.execute_command("show", {})

    def focus(self) -> None:
        """
        Focuses the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.focus()
        """
        return self.execute_command("focus", {})

    def show_and_focus(self) -> None:
        """
        Shows and focuses the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.show_and_focus()
        """
        return self.execute_command("show_and_focus", {})

    def close(self) -> None:
        """
        Closes the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.close()
        """
        return self.execute_command("close", {})

    def fullscreen(self) -> None:
        """
        Enters fullscreen mode.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.fullscreen()
        """
        return self.execute_command("fullscreen", {})

    def toggle_fullscreen(self) -> None:
        """
        Toggles the fullscreen mode of the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.toggle_fullscreen()
        """
        return self.execute_command("toggle_fullscreen", {})

    def minimize(self) -> None:
        """
        Minimizes the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.minimize()
        """
        return self.execute_command("minimize", {})

    def maximize(self) -> None:
        """
        Maximizes the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.maximize()
        """
        return self.execute_command("maximize", {})

    def unmaximize(self) -> None:
        """
        Restores the window from maximized state.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.unmaximize()
        """
        return self.execute_command("unmaximize", {})

    def toggle_maximize(self) -> None:
        """
        Toggles the maximized state of the window.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.toggle_maximize()
        """
        return self.execute_command("toggle_maximize", {})

    def is_fullscreen(self) -> bool:
        """
        Returns True if the window is fullscreen.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.is_fullscreen()
        """
        return self.execute_command("is_fullscreen", {})

    def is_maximized(self) -> bool:
        """
        Returns True if the window is maximized.

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.is_maximized()
        """
        return self.execute_command("is_maximized", {})

    def capture(self, save_path: str) -> "Optional[str]":
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
        """
        return self.execute_command("capture", {"save_path": save_path})

    def add_shortcut(self, key_sequence: str, callback: Callable) -> Any:
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
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> def on_shortcut():
        ...     print("Shortcut activated!")
        >>> window.add_shortcut("Ctrl+C", on_shortcut)
        >>> app.run()
        """
        return self.execute_command("add_shortcut", {"key_sequence": key_sequence, "callback": callback})

    def remove_shortcut(self, key_sequence: str) -> None:
        """
        Removes a keyboard shortcut from the window.

        Parameters
        ----------
        key_sequence : str
            Shortcut sequence to be removed

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.remove_shortcut("Ctrl+C")
        >>> app.run()
        """
        return self.execute_command("remove_shortcut", {"key_sequence": key_sequence})

    def get_all_shortcuts(self) -> dict:
        """
        Returns all registered shortcuts in the window.

        Returns
        -------
        dict
            Dictionary of shortcut sequences and QShortcut objects

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> shortcuts = window.get_all_shortcuts()
        >>> print(shortcuts)
        >>> app.run()
        """
        return self.execute_command("get_all_shortcuts", {})

    def invoke(self, event_name: str, data: "Optional[Dict]" = None) -> None:
        """
        Invokes an event to the JavaScript side.

        Parameters
        ----------
        event_name : str
            Name of the event
        data : dict, optional
            Data to be sent with the event (default is None)

        Examples
        --------
        (Python)
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.invoke("customEvent", {"message": "Hello, Pyloid!"})

        (JavaScript)
        >>> document.addEventListener('customEvent', (data) => {
        ...     console.log(data.message);
        ... });
        """
        return self.execute_command("invoke", {"event_name": event_name, "data": data})

    def get_window_properties(self) -> dict:
        """
        Returns the properties of the window.

        Returns
        -------
        dict
            Dictionary containing the properties of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> properties = window.get_window_properties()
        >>> print(properties)
        >>> app.run()
        """
        return self.execute_command("get_window_properties", {})

    def get_id(self) -> str:
        """
        Returns the ID of the window.

        Returns
        -------
        str
            ID of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window_id = window.get_id()
        >>> print(window_id)
        >>> app.run()
        """
        return self.execute_command("get_id", {})

    def get_size(self) -> "Dict[str, int]":
        """
        Returns the size of the window.

        Returns
        -------
        dict
            Dictionary containing the width and height of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> size = window.get_size()
        >>> print(size)
        >>> app.run()
        """
        return self.execute_command("get_size", {})

    def get_position(self) -> "Dict[str, int]":
        """
        Returns the position of the window.

        Returns
        -------
        dict
            Dictionary containing the x and y coordinates of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> position = window.get_position()
        >>> print(position)
        >>> app.run()
        """
        return self.execute_command("get_position", {})

    def get_title(self) -> str:
        """
        Returns the title of the window.

        Returns
        -------
        str
            Title of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> title = window.get_title()
        >>> print(title)
        >>> app.run()
        """
        return self.execute_command("get_title", {})

    def get_url(self) -> str:
        """
        Returns the URL of the window.

        Returns
        -------
        str
            URL of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> url = window.get_url()
        >>> print(url)
        >>> app.run()
        """
        return self.execute_command("get_url", {})

    def get_visible(self) -> bool:
        """
        Returns the visibility of the window.

        Returns
        -------
        bool
            True if the window is visible, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> visible = window.get_visible()
        >>> print(visible)
        >>> app.run()
        """
        return self.execute_command("get_visible", {})

    def get_frame(self) -> bool:
        """
        Returns the frame enabled state of the window.

        Returns
        -------
        bool
            True if the frame is enabled, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> frame = window.get_frame()
        >>> print(frame)
        >>> app.run()
        """
        return self.execute_command("get_frame", {})

    def set_resizable(self, resizable: bool) -> None:
        """
        Sets the resizability of the window.

        Parameters
        ----------
        resizable : bool
            True to make the window resizable, False to make it fixed size

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_resizable(True)
        >>> app.run()
        """
        return self.execute_command("set_resizable", {"resizable": resizable})

    def set_minimum_size(self, min_width: int, min_height: int) -> None:
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
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_minimum_size(400, 300)
        >>> app.run()
        """
        return self.execute_command("set_minimum_size", {"min_width": min_width, "min_height": min_height})

    def set_maximum_size(self, max_width: int, max_height: int) -> None:
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
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> window.set_maximum_size(1024, 768)
        >>> app.run()
        """
        return self.execute_command("set_maximum_size", {"max_width": max_width, "max_height": max_height})

    def get_minimum_size(self) -> "Dict[str, int]":
        """
        Returns the minimum size of the window.

        Returns
        -------
        dict
            Dictionary containing the minimum width and height of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> min_size = window.get_minimum_size()
        >>> print(min_size)
        >>> app.run()
        """
        return self.execute_command("get_minimum_size", {})

    def get_maximum_size(self) -> "Dict[str, int]":
        """
        Returns the maximum size of the window.

        Returns
        -------
        dict
            Dictionary containing the maximum width and height of the window

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> max_size = window.get_maximum_size()
        >>> print(max_size)
        >>> app.run()
        """
        return self.execute_command("get_maximum_size", {})

    def get_resizable(self) -> bool:
        """
        Returns the resizability of the window.

        Returns
        -------
        bool
            True if the window is resizable, False otherwise

        Examples
        --------
        >>> app = Pyloid(app_name="Pyloid-App")
        >>> window = app.create_window("pyloid-window")
        >>> resizable = window.get_resizable()
        >>> print(resizable)
        >>> app.run()
        """
        return self.execute_command("get_resizable", {})

    def set_static_image_splash_screen(self, image_path: str, close_on_load: bool = True, stay_on_top: bool = True, clickable: bool = True, position: str = "center") -> None:
        """
        Sets the static image splash screen of the window.

        Parameters
        ----------
        image_path : str
            Path to the image file
        close_on_load : bool, optional
            True to close the splash screen when the page is loaded, False otherwise (default is True)
        stay_on_top : bool, optional
            True to keep the splash screen on top, False otherwise (default is True)
        clickable : bool, optional
            True to make the splash screen clickable, False otherwise (default is True)
            if clickable is True, you can click the splash screen to close it.
        position : str, optional
            Position of the splash screen. Options are 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right' (default is 'center')

        Examples
        --------
        >>> window.set_static_image_splash_screen("./assets/loading.png", close_on_load=True, stay_on_top=True)
        """
        return self.execute_command("set_static_image_splash_screen", {
            "image_path": image_path,
            "close_on_load": close_on_load,
            "stay_on_top": stay_on_top,
            "clickable": clickable,
            "position": position
        })

    def set_gif_splash_screen(self, gif_path: str, close_on_load: bool = True, stay_on_top: bool = True, clickable: bool = True, position: str = "center") -> None:
        """
        Sets the gif splash screen of the window.

        Parameters
        ----------
        gif_path : str
            Path to the gif file
        close_on_load : bool, optional
            True to close the splash screen when the page is loaded, False otherwise (default is True)
        stay_on_top : bool, optional
            True to keep the splash screen on top, False otherwise (default is True)
        clickable : bool, optional
            True to make the splash screen clickable, False otherwise (default is True)
            if clickable is True, you can click the splash screen to close it.
        position : str, optional
            Position of the splash screen. Options are 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right' (default is 'center')

        Examples
        --------
        >>> window.set_gif_splash_screen("./assets/loading.gif", close_on_load=True, stay_on_top=True)
        """
        return self.execute_command("set_gif_splash_screen", {
            "gif_path": gif_path,
            "close_on_load": close_on_load,
            "stay_on_top": stay_on_top,
            "clickable": clickable,
            "position": position
        })

    def close_splash_screen(self) -> None:
        """
        Closes the splash screen if it exists.

        Examples
        --------
        >>> window.close_splash_screen()
        """
        return self.execute_command("close_splash_screen", {})
    