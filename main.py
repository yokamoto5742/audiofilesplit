import tkinter as tk

from app.main_window import AudiofilesplitMainWindow


if __name__ == "__main__":
    root = tk.Tk()
    app = AudiofilesplitMainWindow(root)
    root.mainloop()
