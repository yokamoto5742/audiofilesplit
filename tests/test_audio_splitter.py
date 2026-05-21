import subprocess
from math import ceil
from unittest.mock import patch

import pytest

from service.audio_splitter import (
    _calculate_chunks,
    _can_stream_copy,
    _get_output_filename,
    _probe_audio,
    _run_command,
    _split_one_chunk,
    split_audio_file,
)


class TestCalculateChunks:
    """_calculate_chunks関数のテスト"""

    def test_calculate_chunks_exact_division(self):
        """ファイルサイズが目標サイズで割り切れる場合"""
        result = _calculate_chunks(100.0, 25.0)
        assert result == 4

    def test_calculate_chunks_with_remainder(self):
        """ファイルサイズが目標サイズで割り切れない場合"""
        result = _calculate_chunks(100.0, 30.0)
        assert result == 4  # ceil(100/30) = 4

    def test_calculate_chunks_smaller_than_target(self):
        """ファイルサイズが目標サイズより小さい場合"""
        result = _calculate_chunks(10.0, 25.0)
        assert result == 1

    def test_calculate_chunks_equal_to_target(self):
        """ファイルサイズが目標サイズと等しい場合"""
        result = _calculate_chunks(25.0, 25.0)
        assert result == 1

    def test_calculate_chunks_very_large_file(self):
        """非常に大きなファイルの場合"""
        result = _calculate_chunks(1000.0, 24.5)
        assert result == ceil(1000.0 / 24.5)

    def test_calculate_chunks_small_target_size(self):
        """非常に小さい目標サイズの場合"""
        result = _calculate_chunks(100.0, 1.0)
        assert result == 100


class TestGetOutputFilename:
    """_get_output_filename関数のテスト"""

    def test_get_output_filename_basic(self):
        """基本的なファイル名生成"""
        result = _get_output_filename("C:\\test\\audio.mp3", "C:\\output", 0, "m4a")
        assert result == "C:\\output\\audio_part1.m4a"

    def test_get_output_filename_second_chunk(self):
        """2番目のチャンクのファイル名"""
        result = _get_output_filename("C:\\test\\audio.mp3", "C:\\output", 1, "m4a")
        assert result == "C:\\output\\audio_part2.m4a"

    def test_get_output_filename_different_format(self):
        """異なる出力フォーマット"""
        result = _get_output_filename("C:\\test\\audio.mp3", "C:\\output", 0, "mp3")
        assert result == "C:\\output\\audio_part1.mp3"

    def test_get_output_filename_with_extension_in_name(self):
        """拡張子を含むファイル名の処理"""
        result = _get_output_filename("C:\\test\\audio.file.name.mp3", "C:\\output", 5, "m4a")
        assert result == "C:\\output\\audio.file.name_part6.m4a"

    def test_get_output_filename_no_extension(self):
        """拡張子がないファイル"""
        result = _get_output_filename("C:\\test\\audiofile", "C:\\output", 0, "m4a")
        assert result == "C:\\output\\audiofile_part1.m4a"


class TestCanStreamCopy:
    """_can_stream_copy関数のテスト"""

    def test_aac_to_m4a(self):
        """aac入力をm4aへ出力する場合はコピー可能"""
        assert _can_stream_copy("aac", "m4a") is True

    def test_aac_to_mp4(self):
        """aac入力をmp4へ出力する場合はコピー可能"""
        assert _can_stream_copy("aac", "mp4") is True

    def test_mp3_to_mp3(self):
        """mp3入力をmp3へ出力する場合はコピー可能"""
        assert _can_stream_copy("mp3", "mp3") is True

    def test_aac_to_mp3(self):
        """aac入力をmp3へ出力する場合はコピー不可"""
        assert _can_stream_copy("aac", "mp3") is False

    def test_pcm_to_m4a(self):
        """wav(pcm)入力をm4aへ出力する場合はコピー不可"""
        assert _can_stream_copy("pcm_s16le", "m4a") is False

    def test_case_insensitive(self):
        """大文字小文字を区別しない"""
        assert _can_stream_copy("AAC", "M4A") is True

    def test_unknown_format(self):
        """未知の出力フォーマットはコピー不可"""
        assert _can_stream_copy("pcm_s16le", "wav") is False


class TestSplitOneChunk:
    """_split_one_chunk関数のテスト"""

    @patch("service.ffmpeg_runner._run_command")
    def test_stream_copy_uses_copy_codec(self, mock_run):
        """ストリームコピー時は -c copy を使う"""
        _split_one_chunk("in.m4a", "out.m4a", 0.0, 10.0, "m4a", True)
        cmd = mock_run.call_args[0][0]
        assert "-c" in cmd
        assert "copy" in cmd

    @patch("service.ffmpeg_runner._run_command")
    def test_reencode_m4a_uses_aac(self, mock_run):
        """m4a再エンコード時は aac エンコーダを使う"""
        _split_one_chunk("in.wav", "out.m4a", 0.0, 10.0, "m4a", False)
        cmd = mock_run.call_args[0][0]
        assert "-c:a" in cmd
        assert cmd[cmd.index("-c:a") + 1] == "aac"

    @patch("service.ffmpeg_runner._run_command")
    def test_reencode_mp3_uses_libmp3lame(self, mock_run):
        """mp3再エンコード時は libmp3lame エンコーダを使う"""
        _split_one_chunk("in.wav", "out.mp3", 0.0, 10.0, "mp3", False)
        cmd = mock_run.call_args[0][0]
        assert cmd[cmd.index("-c:a") + 1] == "libmp3lame"

    @patch("service.ffmpeg_runner._run_command")
    def test_seek_before_input(self, mock_run):
        """高速シークのため -ss は -i より前に置く"""
        _split_one_chunk("in.m4a", "out.m4a", 5.0, 10.0, "m4a", True)
        cmd = mock_run.call_args[0][0]
        assert cmd.index("-ss") < cmd.index("-i")


class TestRunCommand:
    """_run_command関数のテスト"""

    @patch("service.ffmpeg_runner.subprocess.run", side_effect=FileNotFoundError)
    def test_binary_not_found(self, mock_run):
        """ffmpeg実行ファイルが見つからない場合"""
        with pytest.raises(RuntimeError) as exc_info:
            _run_command(["ffmpeg", "-version"])
        assert "見つかりません" in str(exc_info.value)

    @patch("service.ffmpeg_runner.subprocess.run")
    def test_command_failure(self, mock_run):
        """コマンドが異常終了した場合"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg", stderr="error detail")
        with pytest.raises(RuntimeError) as exc_info:
            _run_command(["ffmpeg", "-version"])
        assert "失敗しました" in str(exc_info.value)


class TestProbeAudio:
    """_probe_audio関数のテスト"""

    @patch("service.ffmpeg_runner._run_command")
    def test_probe_success(self, mock_run):
        """再生時間とコーデック名を取得できる"""
        mock_run.return_value.stdout = "codec_name=aac\nduration=123.45\n"
        duration, codec = _probe_audio("test.m4a")
        assert duration == 123.45
        assert codec == "aac"

    @patch("service.ffmpeg_runner._run_command")
    def test_probe_invalid_duration(self, mock_run):
        """再生時間が取得できない場合はエラー"""
        mock_run.return_value.stdout = "codec_name=aac\nduration=N/A\n"
        with pytest.raises(RuntimeError) as exc_info:
            _probe_audio("test.m4a")
        assert "再生時間" in str(exc_info.value)


class TestSplitAudioFile:
    """split_audio_file関数のテスト"""

    @patch("service.audio_splitter.os.path.getsize")
    def test_no_split_needed(self, mock_getsize):
        """ファイルサイズが目標以下で分割不要な場合"""
        mock_getsize.return_value = 10 * 1024 * 1024  # 10MB
        result = split_audio_file("test.mp3", "output", target_chunk_size_mb=24.5)
        assert result == []

    @patch("service.audio_splitter.os.makedirs")
    @patch("service.audio_splitter._split_one_chunk")
    @patch("service.audio_splitter._probe_audio")
    @patch("service.audio_splitter.os.path.getsize")
    def test_basic_split(self, mock_getsize, mock_probe, mock_split_one, mock_makedirs):
        """基本的な分割処理"""
        mock_getsize.return_value = 50 * 1024 * 1024  # 50MB -> 3チャンク
        mock_probe.return_value = (100.0, "aac")

        result = split_audio_file("test.m4a", "output", target_chunk_size_mb=24.5, output_format="m4a")

        expected_chunks = ceil(50.0 / 24.5)
        assert len(result) == expected_chunks
        assert mock_split_one.call_count == expected_chunks
        mock_makedirs.assert_called_once()

    @patch("service.audio_splitter.os.makedirs")
    @patch("service.audio_splitter._split_one_chunk")
    @patch("service.audio_splitter._probe_audio")
    @patch("service.audio_splitter.os.path.getsize")
    def test_stream_copy_selected(self, mock_getsize, mock_probe, mock_split_one, mock_makedirs):
        """コーデック一致時はストリームコピーを選択する"""
        mock_getsize.return_value = 50 * 1024 * 1024
        mock_probe.return_value = (100.0, "aac")

        split_audio_file("test.m4a", "output", target_chunk_size_mb=24.5, output_format="m4a")

        assert all(call.args[5] is True for call in mock_split_one.call_args_list)

    @patch("service.audio_splitter.os.makedirs")
    @patch("service.audio_splitter._split_one_chunk")
    @patch("service.audio_splitter._probe_audio")
    @patch("service.audio_splitter.os.path.getsize")
    def test_reencode_selected(self, mock_getsize, mock_probe, mock_split_one, mock_makedirs):
        """コーデック不一致時は再エンコードを選択する"""
        mock_getsize.return_value = 50 * 1024 * 1024
        mock_probe.return_value = (100.0, "pcm_s16le")

        split_audio_file("test.wav", "output", target_chunk_size_mb=24.5, output_format="m4a")

        assert all(call.args[5] is False for call in mock_split_one.call_args_list)

    @patch("service.audio_splitter.os.path.getsize", side_effect=FileNotFoundError)
    def test_input_file_not_found(self, mock_getsize):
        """入力ファイルが存在しない場合"""
        with pytest.raises(FileNotFoundError) as exc_info:
            split_audio_file("nonexistent.mp3", "output", target_chunk_size_mb=24.5)
        assert "ファイルが見つかりません" in str(exc_info.value)

    @patch("service.audio_splitter._probe_audio", side_effect=RuntimeError("ffprobe失敗"))
    @patch("service.audio_splitter.os.path.getsize")
    def test_probe_error_propagates(self, mock_getsize, mock_probe):
        """ffprobeでエラーが発生した場合はRuntimeErrorを伝播する"""
        mock_getsize.return_value = 50 * 1024 * 1024
        with pytest.raises(RuntimeError) as exc_info:
            split_audio_file("test.mp3", "output", target_chunk_size_mb=24.5)
        assert "ffprobe失敗" in str(exc_info.value)

    @patch("service.audio_splitter.os.makedirs")
    @patch("service.audio_splitter._split_one_chunk")
    @patch("service.audio_splitter._probe_audio")
    @patch("service.audio_splitter.os.path.getsize")
    def test_progress_callback(self, mock_getsize, mock_probe, mock_split_one, mock_makedirs):
        """進捗コールバックが呼ばれる"""
        mock_getsize.return_value = 50 * 1024 * 1024
        mock_probe.return_value = (100.0, "aac")

        messages: list[str] = []
        split_audio_file(
            "test.m4a", "output",
            target_chunk_size_mb=24.5,
            output_format="m4a",
            progress_callback=messages.append,
        )

        assert len(messages) > 0
        assert any("ファイル:" in msg for msg in messages)
        assert any("完了" in msg for msg in messages)

    @patch("service.audio_splitter.os.path.getsize")
    def test_no_split_with_callback(self, mock_getsize):
        """分割不要な場合のコールバック"""
        mock_getsize.return_value = 10 * 1024 * 1024

        messages: list[str] = []
        result = split_audio_file(
            "test.mp3", "output",
            target_chunk_size_mb=24.5,
            progress_callback=messages.append,
        )

        assert result == []
        assert any("分割は不要" in msg for msg in messages)
