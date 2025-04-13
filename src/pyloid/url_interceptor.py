from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QUrl


# interceptor ( all url request )
class CustomUrlInterceptor(QWebEngineUrlRequestInterceptor):

    def interceptRequest(self, info):
        host = info.requestUrl().host()
        path = info.requestUrl().path()

        server_url = f"http://127.0.0.1:8080"

        if host == "pyloid.local":
            info.redirect(QUrl(f"{server_url}{path}"))
