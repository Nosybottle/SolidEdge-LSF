import logging
from tkinter import messagebox
from typing import Callable


class PopupHandler(logging.Handler):
    """Class for displaying logging errors in a tkinter popup window"""

    def emit(self, record: logging.LogRecord) -> None:
        """Throw a popup warning with the error"""
        raw_message = self.format(record)
        if "|" in raw_message:
            title, message = raw_message.split("|")
        else:
            title = "Error"
            message = raw_message
        messagebox.showwarning(title, message)


class StatusHandler(logging.Handler):
    """Class for displaying info messages in a status bar"""

    def __init__(self, display_info_func: Callable):
        super().__init__()
        self.display_info = display_info_func

    def emit(self, record: logging.LogRecord) -> None:
        """Display formatted message in status bar"""
        message = self.format(record)
        # Don't display warning messages, as they are already displayed (they contain the "|" symbol)
        if "|" in message:
            return
        self.display_info(message)
