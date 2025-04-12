import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional
from .utils import get_free_port

class CustomStaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        pass

def pyloid_serve(
    directory: str,
    port: Optional[int] = None,
) -> str:
    """
    Static file server starts.
    
    Args
    ----
    directory (str): Path to the static file directory to serve
    port (int, optional): Server port (default: None - will use a random free port)
    
    Returns
    -------
    str
        URL of the started server
        
    Examples
    --------
    ```python
    from pyloid import Pyloid
    from pyloid.serve import pyloid_serve
    
    app = Pyloid("Pyloid-App")
    url = pyloid_serve("dist")
    window = app.create_window("Pyloid-App")
    window.load_url(url)
    window.show_and_focus()
    ```
    """
    
    if port is None:
        port = get_free_port()
    
    handler = lambda *args: CustomStaticHandler(*args, directory=directory)
    server = HTTPServer(("127.0.0.1", port), handler)
    
    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )
    thread.start()
    
    return f"http://127.0.0.1:{port}"