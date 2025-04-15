from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QUrl
from typing import Optional

# interceptor ( all url request )
class CustomUrlInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, rpc_url: Optional[str] = None):
        super().__init__()
        self.rpc_url = rpc_url

    def interceptRequest(self, info):
        host = info.requestUrl().host()
        url = info.requestUrl().toString()

        server_url = self.rpc_url
        
        if self.rpc_url is None:
            return
        
        if url.startswith(self.rpc_url):
            return

        if host == "pyloid.rpc":
            info.redirect(QUrl(server_url))
