import os
import subprocess
import tkinter as tk
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from app.main_window import AudiofilesplitMainWindow


@pytest.fixture
def mock_root():
    """Tkinterルートウィンドウのモック"""
    root = Mock(spec=tk.Tk)
    root.title = Mock()
    root.geometry = Mock()
    root.resizable = Mock()
    root.quit = Mock()
    return root


@pytest.fixture
def mock_config():
    """設定ファイルのモック"""
    config = Mock()
    config.getint.side_effect = lambda section, key: {
        ('Appearance', 'window_width'): 400,
        ('Appearance', 'window_height'): 300,
        ('Appearance', 'font_size'): 12,
        ('Audio', 'target_size_mb'): 24,
    }.get((section, key), 0)
    config.get.side_effect = lambda section, key: {
        ('Paths', 'downloads_path'): 'C:\\Downloads',
        ('Paths', 'output_path'): 'C:\\Output',
        ('Audio', 'output_file_format'): 'm4a',
    }.get((section, key), '')
    return config


class TestAudiofilesplitMainWindowInit:
    """AudiofilesplitMainWindow初期化のテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_init_window_setup(self, mock_load_config, mock_button, mock_root, mock_config):
        """ウィンドウの初期設定"""
        mock_load_config.return_value = mock_config

        window = AudiofilesplitMainWindow(mock_root)

        mock_root.title.assert_called_once()
        assert "音声ファイル分割" in mock_root.title.call_args[0][0]
        mock_root.geometry.assert_called_once_with("400x300")
        mock_root.resizable.assert_called_once_with(False, False)

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_init_creates_three_buttons(
        self,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """3つのボタンが作成される"""
        mock_load_config.return_value = mock_config
        mock_button_instance = Mock()
        mock_button.return_value = mock_button_instance

        window = AudiofilesplitMainWindow(mock_root)

        assert mock_button.call_count == 3
        assert mock_button_instance.pack.call_count == 3

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_init_button_labels(self, mock_load_config, mock_button, mock_root, mock_config):
        """ボタンのラベルが正しい"""
        mock_load_config.return_value = mock_config
        mock_button_instance = Mock()
        mock_button.return_value = mock_button_instance

        window = AudiofilesplitMainWindow(mock_root)

        button_texts = [call_args[1]['text'] for call_args in mock_button.call_args_list]
        assert "音声ファイル分割" in button_texts
        assert "設定ファイル" in button_texts
        assert "閉じる" in button_texts


class TestSelectFile:
    """_select_fileメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.filedialog.askopenfilename')
    def test_select_file_success(
        self,
        mock_askopenfilename,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """ファイル選択が成功した場合"""
        mock_load_config.return_value = mock_config
        mock_askopenfilename.return_value = "C:\\test\\audio.mp3"

        window = AudiofilesplitMainWindow(mock_root)
        result = window._select_file(
            "テストタイトル",
            [("MP3", "*.mp3")],
            "C:\\Downloads"
        )

        assert result == "C:\\test\\audio.mp3"
        mock_askopenfilename.assert_called_once_with(
            title="テストタイトル",
            initialdir="C:\\Downloads",
            filetypes=[("MP3", "*.mp3")]
        )

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.filedialog.askopenfilename')
    def test_select_file_cancelled(
        self,
        mock_askopenfilename,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """ファイル選択がキャンセルされた場合"""
        mock_load_config.return_value = mock_config
        mock_askopenfilename.return_value = ""

        window = AudiofilesplitMainWindow(mock_root)
        result = window._select_file(
            "テストタイトル",
            [("MP3", "*.mp3")],
            "C:\\Downloads"
        )

        assert result == ""


class TestOpenOutputDirectory:
    """_open_output_directoryメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.os.startfile')
    @patch('app.main_window.os.path.exists')
    def test_open_output_directory_exists(
        self,
        mock_exists,
        mock_startfile,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """ディレクトリが存在する場合"""
        mock_load_config.return_value = mock_config
        mock_exists.return_value = True

        window = AudiofilesplitMainWindow(mock_root)
        window._open_output_directory("C:\\Output")

        mock_exists.assert_called_once_with("C:\\Output")
        mock_startfile.assert_called_once_with("C:\\Output")

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.os.startfile')
    @patch('app.main_window.os.path.exists')
    def test_open_output_directory_not_exists(
        self,
        mock_exists,
        mock_startfile,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """ディレクトリが存在しない場合"""
        mock_load_config.return_value = mock_config
        mock_exists.return_value = False

        window = AudiofilesplitMainWindow(mock_root)
        window._open_output_directory("C:\\NonExistent")

        mock_exists.assert_called_once_with("C:\\NonExistent")
        mock_startfile.assert_not_called()


class TestHandleErrors:
    """_handle_errorsメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.messagebox.showerror')
    def test_handle_errors_file_not_found(
        self,
        mock_showerror,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """FileNotFoundErrorのハンドリング"""
        mock_load_config.return_value = mock_config

        def raise_file_not_found():
            raise FileNotFoundError("test.mp3")

        window = AudiofilesplitMainWindow(mock_root)
        window._handle_errors(raise_file_not_found)

        mock_showerror.assert_called_once()
        assert "ファイルが見つかりません" in mock_showerror.call_args[0][1]

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.messagebox.showerror')
    def test_handle_errors_general_exception(
        self,
        mock_showerror,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """一般的な例外のハンドリング"""
        mock_load_config.return_value = mock_config

        def raise_exception():
            raise Exception("Generic error")

        window = AudiofilesplitMainWindow(mock_root)
        window._handle_errors(raise_exception)

        mock_showerror.assert_called_once()
        assert "変換中にエラーが発生しました" in mock_showerror.call_args[0][1]

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.messagebox.showerror')
    def test_handle_errors_no_error(
        self,
        mock_showerror,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """エラーが発生しない場合"""
        mock_load_config.return_value = mock_config

        def no_error():
            pass

        window = AudiofilesplitMainWindow(mock_root)
        window._handle_errors(no_error)

        mock_showerror.assert_not_called()


class TestProcessOpenConfig:
    """_process_open_configメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.subprocess.Popen')
    @patch('app.main_window.os.path.exists')
    @patch('app.main_window.CONFIG_PATH', 'C:\\config.ini')
    def test_process_open_config_success(
        self,
        mock_exists,
        mock_popen,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """設定ファイルが存在する場合"""
        mock_load_config.return_value = mock_config
        mock_exists.return_value = True

        window = AudiofilesplitMainWindow(mock_root)
        window._process_open_config()

        mock_exists.assert_called_once_with('C:\\config.ini')
        mock_popen.assert_called_once_with(['notepad.exe', 'C:\\config.ini'])

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.messagebox.showerror')
    @patch('app.main_window.subprocess.Popen')
    @patch('app.main_window.os.path.exists')
    @patch('app.main_window.CONFIG_PATH', 'C:\\config.ini')
    def test_process_open_config_not_found(
        self,
        mock_exists,
        mock_popen,
        mock_showerror,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """設定ファイルが存在しない場合"""
        mock_load_config.return_value = mock_config
        mock_exists.return_value = False

        window = AudiofilesplitMainWindow(mock_root)
        window._process_open_config()

        mock_exists.assert_called_once_with('C:\\config.ini')
        mock_popen.assert_not_called()
        mock_showerror.assert_called_once()
        assert "設定ファイルが見つかりません" in mock_showerror.call_args[0][1]


class TestOpenConfigHandler:
    """open_config_handlerメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_open_config_handler_calls_handle_errors(
        self,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """_handle_errorsを呼び出す"""
        mock_load_config.return_value = mock_config

        window = AudiofilesplitMainWindow(mock_root)
        window._handle_errors = Mock()
        window._process_open_config = Mock()

        window.open_config_handler()

        window._handle_errors.assert_called_once()


class TestSplitAudioHandler:
    """split_audio_handlerメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_split_audio_handler_calls_handle_errors(
        self,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """_handle_errorsを呼び出す"""
        mock_load_config.return_value = mock_config

        window = AudiofilesplitMainWindow(mock_root)
        window._handle_errors = Mock()
        window._process_split_audio = Mock()

        window.split_audio_handler()

        window._handle_errors.assert_called_once()


class TestProcessSplitAudio:
    """_process_split_audioメソッドのテスト"""

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_process_split_audio_cancelled(
        self,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """ファイル選択がキャンセルされた場合"""
        mock_load_config.return_value = mock_config

        window = AudiofilesplitMainWindow(mock_root)
        window._select_file = Mock(return_value="")

        window._process_split_audio()

        window._select_file.assert_called_once()

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.split_audio_file')
    @patch('app.main_window.messagebox.showinfo')
    @patch('app.main_window.os.makedirs')
    @patch('app.main_window.os.path.exists')
    def test_process_split_audio_success(
        self,
        mock_exists,
        mock_makedirs,
        mock_showinfo,
        mock_split_audio_file,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """正常に分割処理が完了する場合"""
        mock_load_config.return_value = mock_config
        mock_exists.return_value = True

        window = AudiofilesplitMainWindow(mock_root)
        window._select_file = Mock(return_value="C:\\test\\audio.mp3")
        window._open_output_directory = Mock()

        window._process_split_audio()

        window._select_file.assert_called_once()
        mock_split_audio_file.assert_called_once_with(
            file_path="C:\\test\\audio.mp3",
            output_dir='C:\\Output',
            target_chunk_size_mb=24,
            output_format='m4a'
        )
        assert mock_showinfo.call_count == 2  # 開始と完了
        window._open_output_directory.assert_called_once_with('C:\\Output')

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    @patch('app.main_window.split_audio_file')
    @patch('app.main_window.messagebox.showinfo')
    @patch('app.main_window.os.makedirs')
    @patch('app.main_window.os.path.exists')
    def test_process_split_audio_creates_output_dir(
        self,
        mock_exists,
        mock_makedirs,
        mock_showinfo,
        mock_split_audio_file,
        mock_load_config,
        mock_button,
        mock_root,
        mock_config
    ):
        """出力ディレクトリが存在しない場合に作成される"""
        mock_load_config.return_value = mock_config
        mock_exists.return_value = False

        window = AudiofilesplitMainWindow(mock_root)
        window._select_file = Mock(return_value="C:\\test\\audio.mp3")
        window._open_output_directory = Mock()

        window._process_split_audio()

        mock_makedirs.assert_called_once_with('C:\\Output', exist_ok=True)

    @patch('app.main_window.tk.Button')
    @patch('app.main_window.load_config')
    def test_process_split_audio_with_different_formats(
        self,
        mock_load_config,
        mock_button,
        mock_root
    ):
        """異なる出力フォーマットのテスト"""
        # MP3フォーマットの設定
        config_mp3 = Mock()
        config_mp3.getint.side_effect = lambda section, key: {
            ('Appearance', 'window_width'): 400,
            ('Appearance', 'window_height'): 300,
            ('Appearance', 'font_size'): 12,
            ('Audio', 'target_size_mb'): 30,
        }.get((section, key), 0)
        config_mp3.get.side_effect = lambda section, key: {
            ('Paths', 'downloads_path'): 'C:\\Downloads',
            ('Paths', 'output_path'): 'C:\\Output',
            ('Audio', 'output_file_format'): 'mp3',
        }.get((section, key), '')

        mock_load_config.return_value = config_mp3

        with patch('app.main_window.split_audio_file') as mock_split:
            with patch('app.main_window.messagebox.showinfo'):
                with patch('app.main_window.os.path.exists', return_value=True):
                    window = AudiofilesplitMainWindow(mock_root)
                    window._select_file = Mock(return_value="C:\\test\\audio.mp3")
                    window._open_output_directory = Mock()

                    window._process_split_audio()

                    mock_split.assert_called_once()
                    call_kwargs = mock_split.call_args[1]
                    assert call_kwargs['output_format'] == 'mp3'
                    assert call_kwargs['target_chunk_size_mb'] == 30
