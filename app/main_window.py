import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

from app import __version__
from utils.config_manager import CONFIG_PATH, load_config


class AudiofilesplitMainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(f"音声ファイル分割 v{__version__}")

        config = load_config()
        window_width = config.getint('Appearance', 'window_width')
        window_height = config.getint('Appearance', 'window_height')
        font_size = config.getint('Appearance', 'font_size')

        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(False, False)

        button_font = ("Yu Gothic UI", font_size)
        button_width = 20
        button_padx = 10
        button_pady = 10

        btn_open_config = tk.Button(
            self.root,
            text="設定ファイル",
            font=button_font,
            width=button_width,
            command=self.open_config_handler
        )
        btn_open_config.pack(pady=button_pady, padx=button_padx)

        btn_close = tk.Button(
            self.root,
            text="閉じる",
            font=button_font,
            width=button_width,
            command=self.root.quit
        )
        btn_close.pack(pady=button_pady, padx=button_padx)

    def _select_file(self, title, filetypes, initialdir):
        """ファイル選択ダイアログを表示"""
        return filedialog.askopenfilename(
            title=title,
            initialdir=initialdir,
            filetypes=filetypes
        )

    def _open_output_directory(self, output_path):
        """出力ディレクトリを開く"""
        if os.path.exists(output_path):
            os.startfile(output_path)

    def _handle_errors(self, func):
        """エラーハンドリングを実行"""
        try:
            func()
        except FileNotFoundError as e:
            messagebox.showerror("エラー", f"ファイルが見つかりません:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました:\n{str(e)}")

    def _process_open_config(self):
        """設定ファイルを開く処理"""
        if os.path.exists(CONFIG_PATH):
            subprocess.Popen(['notepad.exe', CONFIG_PATH])
        else:
            messagebox.showerror("エラー", f"設定ファイルが見つかりません:\n{CONFIG_PATH}")

    def open_config_handler(self):
        """設定ファイルをメモ帳で開く"""
        self._handle_errors(self._process_open_config)
