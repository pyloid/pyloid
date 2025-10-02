from PySide6.QtWebEngineCore import (
	QWebEngineUrlRequestInterceptor,
	QWebEngineUrlRequestInfo,
)


# interceptor ( all url request )
class ServerUrlInterceptor(
	QWebEngineUrlRequestInterceptor
):
	def __init__(
		self,
		server_url: str,
		window_id: str,
	):
		super().__init__()
		self.server_url = server_url
		self.headers = {
			'X-Pyloid-Window-Id': window_id,
		}

		print(
			'interceptor init'
		)

	def interceptRequest(
		self,
		info,
	):
		# host = info.requestUrl().host()
		url = info.requestUrl().toString()

		print(
			url
		)

		if url.startswith(
			self.server_url
		):
			headers = info.httpHeaders()
			print(
				'before',
				headers,
			)
			headers.update(
				self.headers
			)
			print(
				'after',
				headers,
			)
			return
