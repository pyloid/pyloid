import sys
import os
import platform
from typing import Optional
import socket


def get_production_path(path: Optional[str] = None) -> Optional[str]:
    """
    Constructs the absolute path to a resource file, adjusting based on the execution environment.

    In a production environment (e.g., when packaged with PyInstaller or Nuitka),
    it prepends the application's base directory (sys._MEIPASS for PyInstaller,
    or the directory of the executable for Nuitka) to the provided relative path.
    If no path is provided, it returns the base path itself.

    If not running in a production environment (e.g., during development as a regular
    Python script), it simply returns the provided path as is. If no path is provided,
    it returns None in a non-production environment.

    Parameters
    ----------
    path : Optional[str], optional
        The relative path to the resource file from the application's root directory.
        Defaults to None.

    Returns
    -------
    Optional[str]
        - If in production: The absolute path to the resource file (or the base path if `path` is None).
        - If not in production: The original `path` value passed to the function.

    Examples
    --------
    >>> # Assume running NOT in production
    >>> get_production_path("assets/icon.ico")
    'assets/icon.ico'
    >>> get_production_path()
    None

    >>> # Assume running IN production (e.g., PyInstaller bundle)
    >>> # where sys._MEIPASS might be '/tmp/_MEIabcde'
    >>> get_production_path("assets/icon.ico") # doctest: +SKIP
    '/tmp/_MEIabcde/assets/icon.ico'
    >>> get_production_path() # doctest: +SKIP
    '/tmp/_MEIabcde'
    """
    if is_production():
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller
            base_path = sys._MEIPASS
        else:
            # Nuitka
            base_path = os.path.dirname(sys.executable)

            if base_path is None:
                # 환경변수가 없는 경우 실행 파일 디렉토리 사용
                base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

        return os.path.join(base_path, path) if path else base_path
    else:
        return path


def is_production() -> bool:
    """
    Checks if the current environment is a production environment.

    Returns
    -------
    bool
        True if in a production environment, False otherwise.

    Examples
    --------
    >>> from pyloid.utils import is_production
    >>> if is_production():
    >>>     print("Running in production environment.")
    >>> else:
    >>>     print("Not in production environment.")
    """
    # Nuitka 환경 확인을 추가
    if "__compiled__" in globals():
        return True
    # PyInstaller 환경 확인
    return getattr(sys, "frozen", False)


def get_platform() -> str:
    """
    Returns the name of the current system's platform.

    This function uses `platform.system()` to return the name of the current operating system.

    Returns
    -------
    "windows" | "macos" | "linux"
        - "windows" for Windows systems
        - "macos" for macOS systems
        - "linux" for Linux systems

    Examples
    --------
    >>> from pyloid.utils import get_platform
    >>> platform_name = get_platform()
    >>> print(platform_name)
    windows
    """
    os_name = platform.system().lower()
    os_type = {"darwin": "macos", "linux": "linux", "windows": "windows"}.get(os_name)
    if os_type is None:
        raise ValueError(f"Unsupported platform: {os_name}")

    return os_type


def get_absolute_path(path: str) -> str:
    """
    Returns the absolute path of the given relative path.

    Parameters
    ----------
    path : str
        The relative path to get the absolute path of.

    Returns
    -------
    str
        The absolute path of the given relative path.

    Examples
    --------
    >>> from pyloid.utils import get_absolute_path
    >>> absolute_path = get_absolute_path("assets/icon.ico")
    >>> print(absolute_path)
    C:/Users/aaaap/Documents/pyloid/pyloid/assets/icon.ico
    """
    return os.path.normpath(os.path.abspath(path))


def get_free_port() -> int:
    """
    Finds and returns an available random network port number from the operating system.

    This function creates a socket and binds it to port '0', allowing the operating system
    to allocate a random available port. It retrieves the port number and safely closes
    the socket afterward.

    Returns
    -------
    int
        An available network port number (typically in the range 1024-65535)

    Notes
    -----
    - Since this function closes the socket immediately after finding a port, there is a
      possibility that the port could be reassigned to another process.
    - It is recommended to use the port number quickly after receiving it.
    - This function interacts with the operating system's network stack, so its behavior
      may vary depending on firewall or network settings.

    Examples
    --------
    >>> from pyloid.utils import get_free_port
    >>> port = get_free_port()
    >>> print(f"Found available port: {port}")
    Found available port: 49152

    >>> # Web server example
    >>> import http.server
    >>> server = http.server.HTTPServer(('localhost', port), http.server.SimpleHTTPRequestHandler)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def set_qt_backend(backend="software"):
    """
    Sets the Qt Quick backend to force a specific rendering mode.

    This function allows changing the Qt Quick rendering backend by setting
    the QT_QUICK_BACKEND environment variable. Setting it to 'software'
    forces software rendering, which can be useful in environments with
    graphics driver issues or where hardware acceleration is not available.

    Parameters
    ----------
    backend : str, optional
        The backend to use for Qt Quick rendering. Default is 'software'.

    Returns
    -------
    None

    Notes
    -----
    - This setting must be applied before the Qt application is initialized
    - Software rendering may be slower but more compatible across systems

    Examples
    --------
    >>> from pyloid.utils import set_qt_backend
    >>> # Force software rendering
    >>> set_qt_backend("software")
    """
    print(f"Setting QT_QUICK_BACKEND to {backend}.")
    os.environ["QT_QUICK_BACKEND"] = backend
