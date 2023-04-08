import logging
import ctypes
import tkinter as tk

from solidedge import se
from gui.mainapplication import MainApplication
from gui.tklogging import PopupHandler
from config import load_config


def on_close(root: tk.Tk) -> None:
    root.event_generate("<<OnClose>>")
    root.destroy()


def main() -> None:
    # Taskbar icon
    app_id = u"Nosybottle.LSF"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    # Load configuration files
    load_config()

    # Create and hide root window for neater popup errors
    root = tk.Tk()
    root.withdraw()

    # Setup logging
    popup_handler = PopupHandler()
    popup_handler.setLevel(logging.ERROR)
    logger = logging.getLogger("LSF")
    logger.addHandler(popup_handler)

    # Attempt to connect to SolidEdge
    success = se.connect()
    if not success:
        return

    # Create and configure tkinter window
    root.deiconify()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    root.title("SE - Least Squares Fitting")
    root.resizable(False, False)
    root.iconbitmap("icon.ico")

    main_application = MainApplication(root)
    main_application.pack(fill = "both", expand = True)
    root.mainloop()


if __name__ == "__main__":
    main()
