import logging
import ctypes
import tkinter as tk

from gui.mainapplication import MainApplication
from gui.tklogging import PopupHandler


def on_close(root: tk.Tk) -> None:
    root.event_generate("<<OnClose>>")
    root.destroy()


def main() -> None:
    # Taskbar icon
    app_id = u"Nosybottle.LSF"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    # Setup logging
    popup_handler = PopupHandler()
    popup_handler.setLevel(logging.ERROR)
    logger = logging.getLogger("LSF")
    logger.addHandler(popup_handler)

    # Create and configure tkinter window
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    root.title("SE - Least Squares Fitting")
    root.resizable(False, False)
    root.iconbitmap("icon.ico")

    main_application = MainApplication(root)
    main_application.pack(fill = "both", expand = True)
    root.mainloop()


if __name__ == "__main__":
    main()
