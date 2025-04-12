from ..api import PyloidAPI, Bridge

class BaseAPI(PyloidAPI):
    def __init__(self, window_id: str, data: dict):
        super().__init__()
        self.window_id: str = window_id
        self.data: dict = data

    @Bridge(result=dict)
    def getData(self):
        """Returns the shared data of the application."""
        return self.data
    
    @Bridge(result=str)
    def getWindowId(self):
        """Returns the current window ID."""
        return self.window_id
    
    @Bridge()
    def startSystemDrag(self):
        """Starts the system drag."""
        window = self.app.get_window_by_id(self.window_id)
        if window:
            window._window.web_view.start_system_drag()
    
    @Bridge()
    def quit(self):
        """Quits the application."""
        self.app.quit() 