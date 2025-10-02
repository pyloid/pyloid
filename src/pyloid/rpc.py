import asyncio
import json
import logging
import inspect
from functools import (
	wraps,
)
from typing import (
	Any,
	Callable,
	Coroutine,
	Dict,
	List,
	Optional,
	Union,
)
from .utils import (
	get_free_port,
)
from aiohttp import (
	web,
)
import threading
import time
import aiohttp_cors
from typing import (
	TYPE_CHECKING,
)

if TYPE_CHECKING:
	from .pyloid import (
		Pyloid,
	)
	from .browser_window import (
		BrowserWindow,
	)

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('pyloid.rpc')


class RPCContext:
	"""
	Class that provides context information when calling RPC methods.

	Attributes
	----------
	pyloid : Pyloid
	    Pyloid application instance.
	window : BrowserWindow
	    Current browser window instance.
	"""

	def __init__(
		self,
		pyloid: 'Pyloid',
		window: 'BrowserWindow',
	):
		self.pyloid: 'Pyloid' = pyloid
		self.window: 'BrowserWindow' = window


class RPCError(Exception):
	"""
	Custom exception for RPC-related errors.

	Follows the JSON-RPC 2.0 error object structure.

	Attributes
	----------
	message : str
	    A human-readable description of the error.
	code : int, optional
	    A number indicating the error type that occurred. Standard JSON-RPC
	    codes are used where applicable, with application-specific codes
	    also possible. Defaults to -32000 (Server error).
	data : Any, optional
	    Additional information about the error, by default None.
	"""

	def __init__(
		self,
		message: str,
		code: int = -32000,
		data: Any = None,
	):
		"""
		Initialize the RPCError.

		Parameters
		----------
		message : str
		    The error message.
		code : int, optional
		    The error code. Defaults to -32000.
		data : Any, optional
		    Additional data associated with the error. Defaults to None.
		"""
		self.message = message
		self.code = code
		self.data = data
		super().__init__(self.message)

	def to_dict(
		self,
	) -> Dict[
		str,
		Any,
	]:
		"""
		Convert the error details into a dictionary suitable for JSON-RPC responses.

		Returns
		-------
		Dict[str, Any]
		    A dictionary representing the JSON-RPC error object.
		"""
		error_obj = {
			'code': self.code,
			'message': self.message,
		}
		if self.data is not None:
			error_obj['data'] = self.data
		return error_obj


class PyloidRPC:
	"""
	A simple JSON-RPC server wrapper based on aiohttp.

	Allows registering asynchronous functions as RPC methods using the `@rpc`
	decorator and handles JSON-RPC 2.0 request parsing, validation,
	method dispatching, and response formatting.

	Attributes
	----------
	_host : str
	    The hostname or IP address to bind the server to.
	_port : int
	    The port number to listen on.
	_rpc_path : str
	    The URL path for handling RPC requests.
	_functions : Dict[str, Callable[..., Coroutine[Any, Any, Any]]]
	    A dictionary mapping registered RPC method names to their
	    corresponding asynchronous functions.
	_app : web.Application
	    The underlying aiohttp web application instance.
	"""

	def __init__(
		self,
		client_max_size: int = 1024 * 1024 * 10,
	):
		"""
		Initialize the PyloidRPC server instance.

		Parameters
		----------
		client_max_size : int, optional
		    The maximum size of client requests (bytes). Default is 10MB.

		Examples
		--------
		```python
		from pyloid.rpc import (
		    PyloidRPC,
		)

		rpc = PyloidRPC()


		@rpc.method()
		async def add(
		    a: int,
		    b: int,
		) -> int:
		    return a + b
		```
		"""
		self._host = '127.0.0.1'
		self._port = get_free_port()
		self._rpc_path = '/rpc'

		self.url = f'http://{self._host}:{self._port}{self._rpc_path}'

		self._functions: Dict[
			str,
			Callable[
				...,
				Coroutine[
					Any,
					Any,
					Any,
				],
			],
		] = {}
		self._app = web.Application(client_max_size=client_max_size)

		self.pyloid: Optional['Pyloid'] = None
		# self.window: Optional["BrowserWindow"] = None

		# CORS 설정 추가
		cors = aiohttp_cors.setup(
			self._app,
			defaults={
				'*': aiohttp_cors.ResourceOptions(
					allow_credentials=True,
					expose_headers='*',
					allow_headers='*',
					allow_methods=['POST'],
				)
			},
		)

		# CORS 적용된 라우트 추가
		resource = cors.add(self._app.router.add_resource(self._rpc_path))
		cors.add(
			resource.add_route(
				'POST',
				self._handle_rpc,
			)
		)

		log.info(f'RPC server initialized.')
		self._runner: Optional[web.AppRunner] = None
		self._site: Optional[web.TCPSite] = None

	def method(
		self,
		name: Optional[str] = None,
	) -> Callable:
		"""
		Use a decorator to register an async function as an RPC method.

		If there is a 'ctx' parameter, an RPCContext object is automatically injected.
		This object allows access to the pyloid application and current window.

		Parameters
		----------
		name : Optional[str], optional
		    Name to register the RPC method. If None, the function name is used. Default is None.

		Returns
		-------
		Callable
		    The decorator function.

		Raises
		------
		TypeError
		    If the decorated function is not an async function (`coroutinefunction`).
		ValueError
		    If an RPC function with the specified name is already registered.

		Examples
		--------
		```python
		from pyloid.rpc import (
		    PyloidRPC,
		    RPCContext,
		)

		rpc = PyloidRPC()


		@rpc.method()
		async def add(
		    ctx: RPCContext,
		    a: int,
		    b: int,
		) -> int:
		    # Access the application and window through ctx.pyloid and ctx.window
		    if ctx.window:
		        print(f'Window title: {ctx.window.title}')
		    return a + b
		```
		"""

		def decorator(
			func: Callable[
				...,
				Coroutine[
					Any,
					Any,
					Any,
				],
			],
		):
			rpc_name = name or func.__name__
			if not asyncio.iscoroutinefunction(func):
				raise TypeError(f"RPC function '{rpc_name}' must be an async function.")
			if rpc_name in self._functions:
				raise ValueError(f"RPC function name '{rpc_name}' is already registered.")

			# Analyze function signature
			sig = inspect.signature(func)
			has_ctx_param = 'ctx' in sig.parameters

			# Store the original function
			self._functions[rpc_name] = func
			# log.info(f"RPC function registered: {rpc_name}")

			@wraps(func)
			async def wrapper(
				*args,
				_pyloid_window_id=None,
				**kwargs,
			):
				if has_ctx_param and 'ctx' not in kwargs:
					ctx = RPCContext(
						pyloid=self.pyloid,
						window=self.pyloid.get_window_by_id(_pyloid_window_id),
					)
					kwargs['ctx'] = ctx
				return await func(
					*args,
					**kwargs,
				)

			return wrapper

		return decorator

	def _validate_jsonrpc_request(
		self,
		data: Any,
	) -> Optional[
		Dict[
			str,
			Any,
		]
	]:
		"""
		Validate the structure of a potential JSON-RPC request object.

		Checks for required fields ('jsonrpc', 'method') and validates the
		types of fields like 'params' and 'id' according to the JSON-RPC 2.0 spec.

		Parameters
		----------
		data : Any
		    The parsed JSON data from the request body.

		Returns
		-------
		Optional[Dict[str, Any]]
		    None if the request is valid according to the basic structure,
		    otherwise a dictionary representing the JSON-RPC error object
		    to be returned to the client.
		"""
		# Attempt to extract the ID if possible, even for invalid requests
		request_id = (
			data.get('id')
			if isinstance(
				data,
				dict,
			)
			else None
		)

		if not isinstance(
			data,
			dict,
		):
			return {
				'code': -32600,
				'message': 'Invalid Request: Request must be a JSON object.',
			}
		if data.get('jsonrpc') != '2.0':
			return {
				'code': -32600,
				'message': "Invalid Request: 'jsonrpc' version must be '2.0'.",
			}
		if 'method' not in data or not isinstance(
			data['method'],
			str,
		):
			return {
				'code': -32600,
				'message': "Invalid Request: 'method' must be a string.",
			}
		if 'params' in data and not isinstance(
			data['params'],
			(
				list,
				dict,
			),
		):
			# JSON-RPC 2.0: "params" must be array or object if present
			return {
				'code': -32602,
				'message': "Invalid params: 'params' must be an array or object.",
			}
		# JSON-RPC 2.0: "id" is optional, but if present, must be string, number, or null.
		# This validation is simplified here. A more robust check could be added.
		# if "id" in data and not isinstance(data.get("id"), (str, int, float, type(None))):
		#     return {"code": -32600, "message": "Invalid Request: 'id', if present, must be a string, number, or null."}
		return None  # Request structure is valid

	async def _handle_rpc(
		self,
		request: web.Request,
	) -> web.Response:
		"""
		Handles incoming JSON-RPC requests.

		Parses the request, validates it, dispatches to the appropriate
		registered RPC method, executes the method, and returns the
		JSON-RPC response or error object.

		Parameters
		----------
		request : web.Request
		    The incoming aiohttp request object.

		Returns
		-------
		web.Response
		    An aiohttp JSON response object containing the JSON-RPC response or error.
		"""
		request_id: Optional[
			Union[
				str,
				int,
				None,
			]
		] = None
		data: Any = None  # Define data outside try block for broader scope if needed

		try:
			# 1. Check Content-Type
			if request.content_type != 'application/json':
				# Cannot determine ID if content type is wrong, respond with null ID
				error_resp = {
					'jsonrpc': '2.0',
					'error': {
						'code': -32700,
						'message': 'Parse error: Content-Type must be application/json.',
					},
					'id': None,
				}
				return web.json_response(
					error_resp,
					status=415,
				)  # Unsupported Media Type

			# 2. Parse JSON Body
			try:
				raw_data = await request.read()
				data = json.loads(raw_data)
				# Extract ID early for inclusion in potential error responses
				if isinstance(
					data,
					dict,
				):
					request_id = data.get('id')  # Can be str, int, null, or absent
			except json.JSONDecodeError:
				# Invalid JSON, ID might be unknown, respond with null ID
				error_resp = {
					'jsonrpc': '2.0',
					'error': {
						'code': -32700,
						'message': 'Parse error: Invalid JSON format.',
					},
					'id': None,
				}
				return web.json_response(
					error_resp,
					status=400,
				)  # Bad Request

			# 3. Validate JSON-RPC Structure
			validation_error = self._validate_jsonrpc_request(data)
			if validation_error:
				# Use extracted ID if available, otherwise it remains None
				error_resp = {
					'jsonrpc': '2.0',
					'error': validation_error,
					'id': request_id,
				}
				return web.json_response(
					error_resp,
					status=400,
				)  # Bad Request

			# Assuming validation passed, data is a dict with 'method'
			method_name: str = data['method']
			# Use empty list/dict if 'params' is omitted, as per spec flexibility
			params: Union[
				List,
				Dict,
			] = data.get(
				'params',
				[],
			)

			# 4. Find and Call Method
			func = self._functions.get(method_name)
			if func is None:
				error_resp = {
					'jsonrpc': '2.0',
					'error': {
						'code': -32601,
						'message': 'Method not found.',
					},
					'id': request_id,
				}
				return web.json_response(
					error_resp,
					status=404,
				)  # Not Found

			try:
				log.debug(f'Executing RPC method: {method_name}(params={params})')

				# 함수의 서명 분석하여 ctx 매개변수 유무 확인
				sig = inspect.signature(func)
				has_ctx_param = 'ctx' in sig.parameters

				# ctx 매개변수가 있으면 컨텍스트 객체 생성
				if (
					has_ctx_param
					and isinstance(
						params,
						dict,
					)
					and 'ctx' not in params
				):
					ctx = RPCContext(
						pyloid=self.pyloid,
						window=self.pyloid.get_window_by_id(request_id),
					)
					# 딕셔너리 형태로 params 사용할 때
					params = params.copy()  # 원본 params 복사
					params['ctx'] = ctx

				# Call the function with positional or keyword arguments
				if isinstance(
					params,
					list,
				):
					# 리스트 형태로 params 사용할 때 처리 필요
					if has_ctx_param:
						ctx = RPCContext(
							pyloid=self.pyloid,
							window=self.pyloid.get_window_by_id(request_id),
						)
						result = await func(
							ctx,
							*params,
							request_id=request_id,
						)
					else:
						result = await func(
							*params,
							request_id=request_id,
						)
				else:  # isinstance(params, dict)
					internal_window_id = request_id
					params = params.copy()
					params['_pyloid_window_id'] = internal_window_id

					# 함수 시그니처에 맞는 인자만 추려서 전달
					sig = inspect.signature(func)
					allowed_params = set(sig.parameters.keys())
					filtered_params = {k: v for k, v in params.items() if k in allowed_params}
					result = await func(**filtered_params)

				# 5. Format Success Response (only for non-notification requests)
				if request_id is not None:  # Notifications (id=null or absent) don't get responses
					response_data = {
						'jsonrpc': '2.0',
						'result': result,
						'id': request_id,
					}
					return web.json_response(response_data)
				else:
					# No response for notifications, return 204 No Content might be appropriate
					# or just an empty response. aiohttp handles this implicitly if nothing is returned.
					# For clarity/standard compliance, maybe return 204?
					return web.Response(status=204)

			except RPCError as e:
				# Application-specific error during method execution
				log.warning(
					f"RPC execution error in method '{method_name}': {e}",
					exc_info=False,
				)
				if request_id is not None:
					error_resp = {
						'jsonrpc': '2.0',
						'error': e.to_dict(),
						'id': request_id,
					}
					# Use 500 or a more specific 4xx/5xx if applicable based on error code?
					# Sticking to 500 for server-side execution errors.
					return web.json_response(
						error_resp,
						status=500,
					)
				else:
					return web.Response(status=204)  # No response for notification errors
			except Exception as e:
				# Unexpected error during method execution
				log.exception(
					f"Unexpected error during execution of RPC method '{method_name}':"
				)  # Log full traceback
				if request_id is not None:
					# Minimize internal details exposed to the client
					error_resp = {
						'jsonrpc': '2.0',
						'error': {
							'code': -32000,
							'message': f'Server error: {type(e).__name__}',
						},
						'id': request_id,
					}
					return web.json_response(
						error_resp,
						status=500,
					)  # Internal Server Error
				else:
					return web.Response(status=204)  # No response for notification errors

		except Exception as e:
			# Catch-all for fatal errors during request handling itself (before/after method call)
			log.exception('Fatal error in RPC handler:')
			# ID might be uncertain at this stage, include if available
			error_resp = {
				'jsonrpc': '2.0',
				'error': {
					'code': -32603,
					'message': 'Internal error',
				},
				'id': request_id,
			}
			return web.json_response(
				error_resp,
				status=500,
			)

	async def start_async(
		self,
		**kwargs,
	):
		"""Starts the server asynchronously without blocking."""
		self._runner = web.AppRunner(
			self._app,
			access_log=None,
			**kwargs,
		)
		await self._runner.setup()
		self._site = web.TCPSite(
			self._runner,
			self._host,
			self._port,
		)
		await self._site.start()
		log.info(f'RPC server started asynchronously on {self.url}')
		# 서버가 백그라운드에서 실행되도록 여기서 블로킹하지 않습니다.
		# 이 코루틴은 서버 시작 후 즉시 반환됩니다.

	async def stop_async(
		self,
	):
		"""Stops the server asynchronously."""
		if self._runner:
			await self._runner.cleanup()
			log.info('RPC server stopped.')
		self._site = None
		self._runner = None

	def start(
		self,
		**kwargs,
	):
		"""
		Start the aiohttp web server to listen for RPC requests (blocking).

		This method wraps `aiohttp.web.run_app` and blocks until the server stops.
		Prefer `start_async` for non-blocking operation within an asyncio event loop.

		Parameters
		----------
		**kwargs
		    Additional keyword arguments to pass directly to `aiohttp.web.run_app`.
		    For example, `ssl_context` for HTTPS. By default, suppresses the
		    default `aiohttp` startup message using `print=None`.
		"""
		log.info(f'Starting RPC server')
		# Default to print=None to avoid duplicate startup messages, can be overridden via kwargs
		run_app_kwargs = {
			'print': None,
			'access_log': None,
		}
		run_app_kwargs.update(kwargs)
		try:
			web.run_app(
				self._app,
				host=self._host,
				port=self._port,
				**run_app_kwargs,
			)
		except Exception as e:
			log.exception(f'Failed to start or run the server: {e}')
			raise

	def run(
		self,
	):
		"""
		Runs start_async in a separate thread.

		This method is useful when you want to start the aiohttp server in the background
		without blocking the main thread. It creates a new thread, sets up a new asyncio event loop
		in that thread, and starts the asynchronous server. The thread is marked as daemon so that
		it will not prevent the program from exiting if only daemon threads remain.
		"""
		import asyncio

		def _run_asyncio():
			# Create a new event loop for this thread.
			loop = asyncio.new_event_loop()
			# Set the newly created event loop as the current event loop for this thread.
			asyncio.set_event_loop(loop)
			# Start the asynchronous server; this coroutine will set up the server.
			loop.run_until_complete(self.start_async())
			# Keep the event loop running forever to handle incoming requests.
			loop.run_forever()

		# Create a new thread to run the event loop and server in the background.
		# The thread is set as a daemon so it will not block program exit.
		server_thread = threading.Thread(
			target=_run_asyncio,
			daemon=True,
		)
		# Start the background server thread.
		server_thread.start()
