from ..api import PyloidAPI, Bridge

class BaseAPI(PyloidAPI):
    def __init__(self, window_id: str, data: dict):
        super().__init__()
        self.window_id: str = window_id
        self.data: dict = data

    @Bridge(result=str)
    def get_data(self):
        """Returns the shared data of the application."""
        return self.data
    