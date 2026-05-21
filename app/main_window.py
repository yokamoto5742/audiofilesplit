import os
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from app import __version__
from app.progress_window import ProgressWindow
from service.audio_splitter import split_audio_file
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

        self.progress_window: ProgressWindow | None = None
        self._progress_queue: queue.Queue = queue.Queue()

        button_font = ("Yu Gothic UI", font_size)
        button_width = 15
        button_padx = 10
        button_pady = 10

        self.btn_split_audio = tk.Button(
            self.root,
            text="音声ファイル分割",
            font=button_font,
            width=button_width,
            command=self.split_audio_handler
        )
        self.btn_split_audio.pack(pady=button_pady, padx=button_padx)

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

    def split_audio_handler(self):
        """音声ファイル分割ボタンのハンドラ"""
        self._handle_errors(self._process_split_audio)

    def _process_split_audio(self):
        """音声ファイル分割処理(別スレッドで実行)"""
        config = load_config()
        downloads_path = config.get('Paths', 'downloads_path')
        output_path = config.get('Paths', 'output_path')
        target_size_mb = config.getint('Audio', 'target_size_mb')
        output_file_format = config.get('Audio', 'output_file_format')

        # ファイル選択
        filetypes = [
            ("すべての音声ファイル", "*.mp3 *.m4a *.wav *.mp4"),
            ("MP3ファイル", "*.mp3"),
            ("M4Aファイル", "*.m4a"),
            ("WAVファイル", "*.wav"),
            ("すべてのファイル", "*.*")
        ]
        file_path = self._select_file("音声ファイルを選択", filetypes, downloads_path)

        if not file_path:
            return  # キャンセルされた

        # 出力ディレクトリ確認・作成
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        self._progress_queue = queue.Queue()
        self._show_progress_window()
        self.btn_split_audio.config(state=tk.DISABLED)

        # 分割処理はGUIをブロックしないよう別スレッドで実行
        thread = threading.Thread(
            target=self._run_split,
            args=(file_path, output_path, target_size_mb, output_file_format),
            daemon=True
        )
        thread.start()
        self._poll_progress_queue()

    def _show_progress_window(self):
        """進捗表示ウィンドウを作成"""
        self.progress_window = ProgressWindow(self.root)

    def _close_progress_window(self):
        """進捗表示ウィンドウを閉じる"""
        if self.progress_window is not None:
            self.progress_window.close()
            self.progress_window = None

    def _run_split(self, file_path, output_dir, target_size_mb, output_format):
        """別スレッドで分割処理を実行。結果はキュー経由でメインスレッドへ通知する"""
        try:
            split_audio_file(
                file_path=file_path,
                output_dir=output_dir,
                target_chunk_size_mb=target_size_mb,
                output_format=output_format,
                progress_callback=self._on_progress
            )
            self._progress_queue.put(('complete', output_dir))
        except Exception as e:
            self._progress_queue.put(('error', e))

    def _on_progress(self, message):
        """進捗コールバック。root.after を使わずキューに積むだけにする(スレッドセーフ)"""
        self._progress_queue.put(('progress', message))

    def _poll_progress_queue(self):
        """メインスレッドでキューをポーリングし進捗・完了・エラーを処理する"""
        try:
            while True:
                kind, data = self._progress_queue.get_nowait()
                if kind == 'progress':
                    if self.progress_window is not None:
                        self.progress_window.update_message(data)
                elif kind == 'complete':
                    self._on_split_complete(data)
                    return
                elif kind == 'error':
                    self._on_split_error(data)
                    return
        except queue.Empty:
            pass
        self.root.after(50, self._poll_progress_queue)

    def _on_split_complete(self, output_dir):
        """分割完了時の処理"""
        self._close_progress_window()
        self.btn_split_audio.config(state=tk.NORMAL)
        messagebox.showinfo("完了", "音声ファイルの分割が完了しました")
        self._open_output_directory(output_dir)

    def _on_split_error(self, error):
        """分割エラー時の処理"""
        self._close_progress_window()
        self.btn_split_audio.config(state=tk.NORMAL)
        if isinstance(error, FileNotFoundError):
            messagebox.showerror("エラー", f"ファイルが見つかりません:\n{str(error)}")
        else:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました:\n{str(error)}")
