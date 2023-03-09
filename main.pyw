import tkinter as tk

from gui.mainapplication import MainApplication


def on_close(root: tk.Tk):
    root.event_generate("<<OnClose>>")
    root.destroy()


def main():
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))

    main_application = MainApplication(root)
    main_application.pack(fill = "both", expand = True)
    root.mainloop()


if __name__ == "__main__":
    main()
