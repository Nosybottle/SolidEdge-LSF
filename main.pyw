import ctypes
import tkinter as tk

from gui.mainapplication import MainApplication


def on_close(root: tk.Tk):
    root.event_generate("<<OnClose>>")
    root.destroy()


def main():
    # Taskbar icon
    app_id = u"Nosybottle.LSF"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

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
