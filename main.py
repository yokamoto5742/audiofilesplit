import tkinter as tk

from app.main_window import AudiofilesplitMainWindow
from utils.log_rotation import setup_logging


if __name__ == "__main__":
    setup_logging()
    root = tk.Tk()
    app = AudiofilesplitMainWindow(root)
    root.mainloop()
