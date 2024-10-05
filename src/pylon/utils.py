import sys
import os
from typing import Optional


def get_production_path() -> Optional[str]:
    """
    Returns the path to the resource files in a production environment.
    If running as a regular Python script, returns None.

    Returns:
        str | None
    """
    if getattr(sys, 'frozen', False):
        # If built with PyInstaller
        return os.path.join(sys._MEIPASS)
    else:
        # If running as a regular Python script
        return None


def is_production():
    """
    Checks if the current environment is a production environment.

    Returns:
        bool: True if in a production environment, False otherwise.
    """
    return getattr(sys, 'frozen', False)
