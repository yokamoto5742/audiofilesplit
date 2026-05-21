import tkinter as tk


class ProgressWindow:
    """分割処理中の進捗を表示する Toplevel ウィンドウ"""

    def __init__(self, parent: tk.Tk) -> None:
        self._window = tk.Toplevel(parent)
        self._window.title("処理中")
        self._window.geometry("360x100")
        self._window.resizable(False, False)
        self._window.transient(parent)

        self._label = tk.Label(
            self._window,
            text="音声ファイルの分割を開始します",
            font=("Yu Gothic UI", 9),
            wraplength=340
        )
        self._label.pack(expand=True, padx=10, pady=10)

    def update_message(self, message: str) -> None:
        """ラベルのテキストを更新"""
        self._label.config(text=message)

    def close(self) -> None:
        """ウィンドウを破棄"""
        self._window.destroy()
