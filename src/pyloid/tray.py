from enum import Enum
from PySide6.QtWidgets import QSystemTrayIcon


class TrayEvent(Enum):
    """
    TrayEvent is an enumeration class representing events related to the system tray icon.

    Enumeration Members
    -------------------
    DoubleClick : Event that occurs when the tray icon is double-clicked
    MiddleClick : Event that occurs when the tray icon is clicked with the middle button
    RightClick : Event that occurs when the tray icon is right-clicked (context menu)
    LeftClick : Event that occurs when the tray icon is left-clicked
    Unknown : Unknown event

    Usage Example
    -------------
    ```python
    from pyloid import Pyloid, TrayEvent

    app = Pyloid(app_name="Pyloid-App")

    app.set_tray_icon("icons/icon.ico")

    app.set_tray_actions(
        {
        TrayEvent.DoubleClick: lambda: print("Tray icon was double-clicked."),
        TrayEvent.MiddleClick: lambda: print("Tray icon was middle-clicked."),
        TrayEvent.RightClick: lambda: print("Tray icon was right-clicked."),
        TrayEvent.LeftClick: lambda: print("Tray icon was left-clicked."),
        }
    )
    ```
    """
    DoubleClick = QSystemTrayIcon.ActivationReason.DoubleClick
    MiddleClick = QSystemTrayIcon.ActivationReason.MiddleClick
    RightClick = QSystemTrayIcon.ActivationReason.Context
    LeftClick = QSystemTrayIcon.ActivationReason.Trigger
    Unknown = QSystemTrayIcon.ActivationReason.Unknown

    def __eq__(self, other):
        if isinstance(other, QSystemTrayIcon.ActivationReason):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)
