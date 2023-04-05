import logging
from tkinter import messagebox


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
