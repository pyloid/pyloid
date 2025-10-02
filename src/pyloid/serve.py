import threading
import asyncio
import mimetypes
import aiofiles
from aiohttp import web
from aiohttp.web_fileresponse import FileResponse
from typing import Optional
from pathlib import Path
from .utils import get_free_port, is_production
import logging

logging.getLogger('aiohttp').setLevel(logging.WARNING)


class ZeroCopyFileResponse(FileResponse):
    """zero-copy optimized file response class"""
    
    def __init__(self, path, chunk_size=65536, headers=None):
        """
        Args:
            path: file path
            chunk_size: streaming chunk size (64KB default)
            headers: additional HTTP headers
        """
        super().__init__(path, chunk_size=chunk_size, headers=headers)
        self._enable_sendfile = True  # sendfile() system call activation


class ZeroCopyStaticHandler:
    """zero-copy optimized static file handler"""
    
    def __init__(self, directory: str):
        self.directory = Path(directory).resolve()
        self.chunk_size = 65536  # 64KB chunk
        
    async def handle_request(self, request):
        """HTTP request processing"""
        try:
            # URL path parsing
            path = request.path_qs.split('?')[0]  # remove query parameters
            if path.endswith('/'):
                path += 'index.html'
            
            # Security: prevent directory traversal attacks
            file_path = (self.directory / path.lstrip('/')).resolve()
            if not str(file_path).startswith(str(self.directory)):
                return web.Response(status=403, text="Forbidden")
            
            # Check if the file exists
            if not file_path.exists() or not file_path.is_file():
                return web.Response(status=404, text="File not found")
            
            # Check the file size and type
            stat = file_path.stat()
            file_size = stat.st_size
            content_type, _ = mimetypes.guess_type(str(file_path))
            
            # Range request processing (partial download supported)
            range_header = request.headers.get('Range')
            if range_header:
                return await self._handle_range_request(file_path, range_header, file_size, content_type, request)
            
            if is_production():
                cache_control = 'public, max-age=3600'  # 1 hour caching
            else:
                cache_control = 'no-cache'
                
            # zero-copy file response creation
            headers = {
                'Content-Type': content_type or 'application/octet-stream',
                'Content-Length': str(file_size),
                'Accept-Ranges': 'bytes',
                'Cache-Control': cache_control,
                'ETag': f'"{stat.st_mtime}-{file_size}"'
            }
            
            # ETag based cache check
            if_none_match = request.headers.get('If-None-Match')
            if if_none_match == headers['ETag']:
                return web.Response(status=304, headers=headers)
            
            # zero-copy response return (sendfile used)
            return ZeroCopyFileResponse(
                path=file_path,
                chunk_size=self.chunk_size,
                headers=headers
            )
            
        except Exception as e:
            return web.Response(status=500, text=f"Internal Server Error: {str(e)}")
    
    async def _handle_range_request(self, file_path, range_header, file_size, content_type, request):
        """Range request processing (partial download)"""
        try:
            # Range header parsing: bytes=start-end
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Range validation
            if start >= file_size or end >= file_size or start > end:
                return web.Response(
                    status=416,  # Range Not Satisfiable
                    headers={'Content-Range': f'bytes */{file_size}'}
                )
            
            content_length = end - start + 1
            
            headers = {
                'Content-Type': content_type or 'application/octet-stream',
                'Content-Length': str(content_length),
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes'
            }
            
            # zero-copy partial response
            response = web.StreamResponse(status=206, headers=headers)
            await response.prepare(request)
            
            # aiofiles to async zero-copy transfer
            async with aiofiles.open(file_path, 'rb') as f:
                await f.seek(start)
                remaining = content_length
                
                while remaining > 0:
                    chunk_size = min(self.chunk_size, remaining)
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    await response.write(chunk)
                    remaining -= len(chunk)
            
            await response.write_eof()
            return response
            
        except Exception as e:
            return web.Response(status=500, text=f"Range Request Error: {str(e)}")


async def start_zero_copy_server(directory: str, port: int):
    """zero-copy optimized server starts"""
    handler = ZeroCopyStaticHandler(directory)
    
    # aiohttp app creation
    app = web.Application()
    app.router.add_route('GET', '/{path:.*}', handler.handle_request)
    
    # server configuration optimization
    runner = web.AppRunner(
        app,
        access_log=None,  # access log disabled (performance improvement)
        keepalive_timeout=75,  # Keep-Alive timeout
        client_timeout=600,    # client timeout
    )
    
    await runner.setup()
    
    site = web.TCPSite(
        runner, 
        '127.0.0.1', 
        port,
        backlog=1024,  # connection backlog size
        reuse_address=True  # port reuse only
    )
    
    await site.start()
    
    return runner, site


def pyloid_serve(
    directory: str,
    port: Optional[int] = None,
) -> str:
    """
    zero-copy optimized static file server starts.
    
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
    
    def run_zero_copy_server():
        """run async server in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            runner, site = loop.run_until_complete(
                start_zero_copy_server(directory, port)
            )
            
            print(f"🚀 Zero-copy frontend server started on http://127.0.0.1:{port}")
            print(f"📁 Serving directory: {directory}")
            print(f"⚡ Features: sendfile, Range requests, ETag caching")
            
            # wait until the server starts
            loop.run_forever()
            
        except Exception as e:
            print(f"Zero-copy server error: {e}")
        finally:
            loop.close()
    
    # start server in a daemon thread
    thread = threading.Thread(target=run_zero_copy_server, daemon=True)
    thread.start()
    
    return f"http://127.0.0.1:{port}"