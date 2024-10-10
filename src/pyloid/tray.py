from enum import Enum
from PySide6.QtWidgets import QSystemTrayIcon


class TrayEvent(Enum):
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
