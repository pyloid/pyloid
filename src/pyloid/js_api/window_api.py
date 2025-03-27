# from typing import TYPE_CHECKING, Optional

# from ..api import PyloidAPI, Bridge
# from PySide6.QtCore import QByteArray, QBuffer, QIODeviceBase
# import base64

# if TYPE_CHECKING:
#     from ..pyloid import Pyloid

# class WindowAPI(PyloidAPI):
#     # def __init__(self, window_id: str, app: 'Pyloid'):
#     #     super().__init__()
#     #     self.window_id: str = window_id
#     #     self.app: 'Pyloid' = app

#     @Bridge(result=str)
#     def getWindowId(self):
#         """Returns the current window ID."""
#         return self.window_id

#     @Bridge(result=dict)
#     def getWindowProperties(self):
#         """Returns the properties of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         window_properties = window.get_window_properties()
#         return window_properties

#     @Bridge()
#     def close(self):
#         """Closes the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.close()

#     @Bridge()
#     def hide(self):
#         """Hides the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.hide()

#     @Bridge()
#     def show(self):
#         """Shows and focuses the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.show()

#     @Bridge()
#     def focus(self):
#         """Focuses the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.focus()

#     @Bridge()
#     def showAndFocus(self):
#         """Shows and focuses the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.show_and_focus()

#     @Bridge()
#     def fullscreen(self):
#         """Enters fullscreen mode."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.fullscreen()

#     @Bridge()
#     def toggleFullscreen(self):
#         """Toggles fullscreen mode for the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.toggle_fullscreen()

#     @Bridge()
#     def minimize(self):
#         """Minimizes the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.minimize()

#     @Bridge()
#     def maximize(self):
#         """Maximizes the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.maximize()

#     @Bridge()
#     def unmaximize(self):
#         """Restores the window to its normal state."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.unmaximize()

#     @Bridge()
#     def toggleMaximize(self):
#         """Toggles the maximized state of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.toggle_maximize()

#     @Bridge(result=bool)
#     def isFullscreen(self):
#         """Returns True if the window is fullscreen."""
#         window = self.app.get_window_by_id(self.window_id)
#         return window.is_fullscreen()
    
#     @Bridge(result=bool)
#     def isMaximized(self):
#         """Returns True if the window is maximized."""
#         window = self.app.get_window_by_id(self.window_id)
#         return window.is_maximized()

#     @Bridge(str)
#     def setTitle(self, title: str):
#         """Sets the title of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.set_title(title)

#     @Bridge(int, int)
#     def setSize(self, width: int, height: int):
#         """Sets the size of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.set_size(width, height)

#     @Bridge(int, int)
#     def setPosition(self, x: int, y: int):
#         """Sets the position of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.set_position(x, y)

#     @Bridge(bool)
#     def setFrame(self, frame: bool):
#         """Sets the frame of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.set_frame(frame)

#     @Bridge(bool)
#     def setContextMenu(self, context_menu: bool):
#         """Sets the context menu of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.set_context_menu(context_menu)

#     @Bridge(bool)
#     def setDevTools(self, enable: bool):
#         """Sets the developer tools of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.set_dev_tools(enable)

#     @Bridge(str, result=Optional[str])
#     def capture(self, save_path: str) -> Optional[str]:
#         """Captures the current window."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             return window.capture(save_path)
#         return None

#     @Bridge(result=bool)
#     def getFrame(self):
#         """Returns whether the window has a frame."""
#         window = self.app.get_window_by_id(self.window_id)
#         return window.frame if window else False

#     @Bridge(result=bool)
#     def getContextMenu(self):
#         """Returns whether the window has a context menu."""
#         window = self.app.get_window_by_id(self.window_id)
#         return window.context_menu if window else False

#     @Bridge(result=bool)
#     def getDevTools(self):
#         """Returns whether the window has developer tools."""
#         window = self.app.get_window_by_id(self.window_id)
#         return window.dev_tools if window else False

#     @Bridge(result=str)
#     def getTitle(self):
#         """Returns the title of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         return window.title if window else ""

#     @Bridge(result=dict)
#     def getSize(self):
#         """Returns the size of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         return (
#             {"width": window.width, "height": window.height}
#             if window
#             else {"width": 0, "height": 0}
#         )

#     @Bridge(result=dict)
#     def getPosition(self):
#         """Returns the position of the window."""
#         window = self.app.get_window_by_id(self.window_id)
#         return {"x": window.x, "y": window.y} if window else {"x": 0, "y": 0}

#     @Bridge()
#     def startSystemDrag(self):
#         """Starts the system drag."""
#         window = self.app.get_window_by_id(self.window_id)
#         if window:
#             window.web_view.start_system_drag()

#     ###############################################################
#     # Clipboard
#     ###############################################################

#     @Bridge(str)
#     def setClipboardText(self, text: str):
#         """Sets the text to the clipboard."""
#         self.app.set_clipboard_text(text)

#     @Bridge(result=str)
#     def getClipboardText(self):
#         """Gets the text from the clipboard."""
#         return self.app.get_clipboard_text()
    
#     @Bridge(str, str)
#     def setClipboardImage(self, image_path: str, format: str):
#         """Sets the image to the clipboard."""
#         self.app.set_clipboard_image(image_path, format)

#     @Bridge(result=str)
#     def getClipboardImage(self):
#         """클립보드의 이미지를 Base64 인코딩된 데이터 URL로 반환합니다."""
#         image = self.app.get_clipboard_image()  # QImage 반환 가정
#         if image and not image.isNull():
#             # QImage를 바이트 배열로 변환
#             byte_array = QByteArray()
#             buffer = QBuffer(byte_array)
#             buffer.open(QIODeviceBase.WriteOnly)
#             image.save(buffer, "PNG")  # PNG 형식으로 저장
            
#             # Base64로 인코딩
#             base64_data = byte_array.toBase64().data().decode()
#             return f"data:image/png;base64,{base64_data}"
#         return ""
    
#     ###########################################################################################
#     # Quit
#     ###########################################################################################
#     @Bridge()
#     def quit(self):
#         """Quits the application."""
#         self.app.quit()
        

    
