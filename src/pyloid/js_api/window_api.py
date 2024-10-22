from ..api import PyloidAPI, Bridge
from typing import Optional

class WindowAPI(PyloidAPI):
    def __init__(self, window_id: str, app):
        super().__init__()
        self.window_id: str = window_id
        self.app = app

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