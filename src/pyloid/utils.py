import sys
import os
import platform
from typing import Optional


def get_production_path() -> Optional[str]:
    """
    Returns the path to the resource files in a production environment.
    If running as a regular Python script, returns None.

    Returns
    -------
    str | None
        The path to the resource files if in a production environment, 
        otherwise None.

    Examples
    --------
    >>> from pyloid.utils import get_production_path
    >>> path = get_production_path()
    >>> if path:
    >>>     print(f"Production path: {path}")
    >>> else:
    >>>     print("Not in a production environment.")
    """
    if getattr(sys, 'frozen', False):
        # If built with PyInstaller
        return sys._MEIPASS
    else:
        # If running as a regular Python script
        return None

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
    return getattr(sys, 'frozen', False)


def get_platform() -> str:
    """
    Returns the name of the current system's platform.

    This function uses `platform.system()` to return the name of the current operating system.

    Returns
    -------
    "Windows" | "Darwin" | "Linux"
        - "Windows" for Windows systems
        - "Darwin" for macOS systems
        - "Linux" for Linux systems

    Examples
    --------
    >>> from pyloid.utils import get_platform
    >>> platform_name = get_platform()
    >>> print(platform_name)
    Windows
    """
    return platform.system()




