import logging
import ctypes
import tkinter as tk
import sys
from typing import Callable

from solidedge import se
from gui.mainapplication import MainApplication
from gui.tklogging import PopupHandler, StatusHandler
from config import load_config, lang


def setup_popup_logging(logger: logging.Logger) -> None:
    """Configure logger to display WARNING as popup windows"""
    popup_handler = PopupHandler()
    popup_handler.setLevel(logging.ERROR)
    logger.addHandler(popup_handler)


def setup_status_bar_logging(logger: logging.Logger, display_info_func: Callable) -> None:
    """Configure logger to display INFO in GUI label"""
    status_handler = StatusHandler(display_info_func)
    status_handler.setLevel(logging.INFO)
    logger.addHandler(status_handler)


def on_close(root: tk.Tk) -> None:
    root.event_generate("<<OnClose>>")
    root.destroy()


def main() -> None:
    # Setup logging
    logger = logging.getLogger("LSF")
    logger.setLevel(logging.INFO)
    std_handler = logging.StreamHandler(sys.stderr)
    std_handler.setLevel(logging.NOTSET)
    logger.addHandler(std_handler)

    # Taskbar icon
    app_id = u"Nosybottle.LSF"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    # Create and hide root window for neater popup errors
    root = tk.Tk()
    root.withdraw()

    # Error logging
    setup_popup_logging(logger)

    # Load configuration files
    if not load_config():
        return

    # Attempt to connect to SolidEdge
    success = se.connect()
    if not success:
        return

    # Create and configure tkinter window
    root.deiconify()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    root.title(lang.app.title)
    root.resizable(False, False)
    root.iconbitmap("icon.ico")

    main_application = MainApplication(root)
    main_application.pack(fill = "both", expand = True)

    # Info logging
    setup_status_bar_logging(logger, main_application.set_info_display)

    root.mainloop()


if __name__ == "__main__":
    main()
