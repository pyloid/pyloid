from typing import TYPE_CHECKING, Optional

from ..api import PyloidAPI, Bridge
from PySide6.QtCore import QByteArray, QBuffer, QIODeviceBase
import base64
from ..utils import get_platform, is_production, get_production_path

if TYPE_CHECKING:
    from ..pyloid import Pyloid


class BaseAPI(PyloidAPI):
    def __init__(self, window_id: str, data: dict, app: "Pyloid"):
        super().__init__()
        self.window_id: str = window_id
        self.data: dict = data
        self.app: "Pyloid" = app

    @Bridge(result=dict)
    def getData(self):
        """Returns the shared data of the application."""
        return self.data

    @Bridge()
    def startSystemDrag(self):
        """Starts the system drag."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window._window.web_view.start_system_drag()

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
    def focus(self):
        """Focuses the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.focus()

    @Bridge()
    def showAndFocus(self):
        """Shows and focuses the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.show_and_focus()

    @Bridge()
    def fullscreen(self):
        """Enters fullscreen mode."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.fullscreen()

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

    @Bridge()
    def toggleMaximize(self):
        """Toggles the maximized state of the window."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window.toggle_maximize()

    @Bridge(result=bool)
    def isFullscreen(self):
        """Returns True if the window is fullscreen."""
        window = self.app.get_window_by_id(self.window_id)
        return window.is_fullscreen()

    @Bridge(result=bool)
    def isMaximized(self):
        """Returns True if the window is maximized."""
        window = self.app.get_window_by_id(self.window_id)
        return window.is_maximized()

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

    @Bridge(result=bool)
    def getFrame(self):
        """Returns whether the window has a frame."""
        window = self.app.get_window_by_id(self.window_id)
        return window.frame if window else False

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

    ###############################################################
    # Clipboard
    ###############################################################

    @Bridge(str)
    def setClipboardText(self, text: str):
        """Sets the text to the clipboard."""
        self.app.set_clipboard_text(text)

    @Bridge(result=str)
    def getClipboardText(self):
        """Gets the text from the clipboard."""
        return self.app.get_clipboard_text()

    @Bridge(str, str)
    def setClipboardImage(self, image_path: str, format: str):
        """Sets the image to the clipboard."""
        self.app.set_clipboard_image(image_path, format)

    @Bridge(result=str)
    def getClipboardImage(self):
        """Returns the clipboard image as a Base64 encoded data URL."""
        image = self.app.get_clipboard_image()  # Assuming it returns QImage
        if image and not image.isNull():
            # Convert QImage to byte array
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODeviceBase.WriteOnly)
            image.save(buffer, "PNG")  # Save in PNG format

            # Encode to Base64
            base64_data = byte_array.toBase64().data().decode()
            return f"data:image/png;base64,{base64_data}"
        return ""

    ###########################################################################################
    # Quit
    ###########################################################################################
    @Bridge()
    def quit(self):
        """Quits the application."""
        self.app.quit()

    ###########################################################################################
    # Utils
    ###########################################################################################
    @Bridge(result=str)
    def getPlatform(self):
        """Returns the platform of the application.

        Returns
        -------
        str
            The platform of the application (windows, linux, macos)
        """
        return get_platform()

    @Bridge(result=bool)
    def isProduction(self):
        """Returns True if the application is in production mode."""
        return is_production()

    @Bridge(str, result=str)
    def getProductionPath(self, path: str):
        """Returns the production path of the application."""
        return get_production_path(path)
    
    
