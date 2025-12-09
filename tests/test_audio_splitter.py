import os
from math import ceil
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydub import AudioSegment

from service.audio_splitter import (
    _calculate_chunks,
    _export_chunk,
    _get_output_filename,
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
        result = _get_output_filename(
            "C:\\test\\audio.mp3",
            "C:\\output",
            0,
            "m4a"
        )
        assert result == "C:\\output\\audio_part1.m4a"

    def test_get_output_filename_second_chunk(self):
        """2番目のチャンクのファイル名"""
        result = _get_output_filename(
            "C:\\test\\audio.mp3",
            "C:\\output",
            1,
            "m4a"
        )
        assert result == "C:\\output\\audio_part2.m4a"

    def test_get_output_filename_different_format(self):
        """異なる出力フォーマット"""
        result = _get_output_filename(
            "C:\\test\\audio.mp3",
            "C:\\output",
            0,
            "mp3"
        )
        assert result == "C:\\output\\audio_part1.mp3"

    def test_get_output_filename_with_extension_in_name(self):
        """拡張子を含むファイル名の処理"""
        result = _get_output_filename(
            "C:\\test\\audio.file.name.mp3",
            "C:\\output",
            5,
            "m4a"
        )
        assert result == "C:\\output\\audio.file.name_part6.m4a"

    def test_get_output_filename_no_extension(self):
        """拡張子がないファイル"""
        result = _get_output_filename(
            "C:\\test\\audiofile",
            "C:\\output",
            0,
            "m4a"
        )
        assert result == "C:\\output\\audiofile_part1.m4a"


class TestExportChunk:
    """_export_chunk関数のテスト"""

    @patch.object(AudioSegment, 'export')
    def test_export_chunk_m4a_format(self, mock_export):
        """m4a形式でのエクスポート"""
        mock_chunk = Mock(spec=AudioSegment)
        _export_chunk(mock_chunk, "output.m4a", "m4a")
        mock_chunk.export.assert_called_once_with(
            "output.m4a",
            format="mp4",
            codec="aac"
        )

    @patch.object(AudioSegment, 'export')
    def test_export_chunk_mp4_format(self, mock_export):
        """mp4形式でのエクスポート"""
        mock_chunk = Mock(spec=AudioSegment)
        _export_chunk(mock_chunk, "output.mp4", "mp4")
        mock_chunk.export.assert_called_once_with(
            "output.mp4",
            format="mp4",
            codec="aac"
        )

    @patch.object(AudioSegment, 'export')
    def test_export_chunk_mp3_format(self, mock_export):
        """mp3形式でのエクスポート"""
        mock_chunk = Mock(spec=AudioSegment)
        _export_chunk(mock_chunk, "output.mp3", "mp3")
        mock_chunk.export.assert_called_once_with(
            "output.mp3",
            format="mp3"
        )

    @patch.object(AudioSegment, 'export')
    def test_export_chunk_other_format(self, mock_export):
        """その他の形式でのエクスポート"""
        mock_chunk = Mock(spec=AudioSegment)
        _export_chunk(mock_chunk, "output.wav", "wav")
        mock_chunk.export.assert_called_once_with(
            "output.wav",
            format="wav"
        )

    @patch.object(AudioSegment, 'export')
    def test_export_chunk_uppercase_format(self, mock_export):
        """大文字のフォーマット指定"""
        mock_chunk = Mock(spec=AudioSegment)
        _export_chunk(mock_chunk, "output.M4A", "M4A")
        mock_chunk.export.assert_called_once_with(
            "output.M4A",
            format="mp4",
            codec="aac"
        )


class TestSplitAudioFile:
    """split_audio_file関数のテスト"""

    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    def test_split_audio_file_no_split_needed(self, mock_getsize, mock_exists):
        """ファイルサイズが目標以下で分割不要な場合"""
        mock_getsize.return_value = 10 * 1024 * 1024  # 10MB
        mock_exists.return_value = True

        result = split_audio_file(
            "test.mp3",
            "output",
            target_chunk_size_mb=24.5,
            output_format="m4a"
        )

        assert result == []

    @patch('service.audio_splitter.os.makedirs')
    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    @patch('service.audio_splitter.AudioSegment.from_file')
    @patch('service.audio_splitter._export_chunk')
    def test_split_audio_file_basic_split(
        self,
        mock_export,
        mock_from_file,
        mock_getsize,
        mock_exists,
        mock_makedirs
    ):
        """基本的な分割処理"""
        # ファイルサイズ: 50MB -> ceil(50/24.5) = 3チャンクに分割
        mock_getsize.return_value = 50 * 1024 * 1024
        mock_exists.return_value = False

        # モックオーディオセグメント (10秒 = 10000ms)
        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 10000
        mock_audio.__getitem__.return_value = MagicMock()
        mock_from_file.return_value = mock_audio

        result = split_audio_file(
            "test.mp3",
            "output",
            target_chunk_size_mb=24.5,
            output_format="m4a"
        )

        expected_chunks = ceil(50.0 / 24.5)
        assert len(result) == expected_chunks
        assert mock_export.call_count == expected_chunks
        mock_makedirs.assert_called_once()

    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    def test_split_audio_file_not_found(self, mock_getsize, mock_exists):
        """入力ファイルが存在しない場合"""
        mock_getsize.side_effect = FileNotFoundError("File not found")
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as exc_info:
            split_audio_file(
                "nonexistent.mp3",
                "output",
                target_chunk_size_mb=24.5
            )

        assert "ファイルが見つかりません" in str(exc_info.value)

    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    @patch('service.audio_splitter.AudioSegment.from_file')
    def test_split_audio_file_pydub_error(
        self,
        mock_from_file,
        mock_getsize,
        mock_exists
    ):
        """pydubでエラーが発生した場合"""
        mock_getsize.return_value = 50 * 1024 * 1024
        mock_exists.return_value = True
        mock_from_file.side_effect = Exception("pydub error")

        with pytest.raises(RuntimeError) as exc_info:
            split_audio_file(
                "test.mp3",
                "output",
                target_chunk_size_mb=24.5
            )

        assert "処理中にエラーが発生しました" in str(exc_info.value)
        assert "ffmpeg" in str(exc_info.value)

    @patch('service.audio_splitter.os.makedirs')
    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    @patch('service.audio_splitter.AudioSegment.from_file')
    @patch('service.audio_splitter._export_chunk')
    def test_split_audio_file_with_progress_callback(
        self,
        mock_export,
        mock_from_file,
        mock_getsize,
        mock_exists,
        mock_makedirs
    ):
        """進捗コールバック付きの分割処理"""
        mock_getsize.return_value = 50 * 1024 * 1024
        mock_exists.return_value = False

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 10000
        mock_audio.__getitem__.return_value = MagicMock()
        mock_from_file.return_value = mock_audio

        progress_messages = []

        def progress_callback(msg):
            progress_messages.append(msg)

        result = split_audio_file(
            "test.mp3",
            "output",
            target_chunk_size_mb=24.5,
            output_format="m4a",
            progress_callback=progress_callback
        )

        expected_chunks = ceil(50.0 / 24.5)
        assert len(result) == expected_chunks
        assert len(progress_messages) > 0
        assert any("ファイル:" in msg for msg in progress_messages)
        assert any("読み込んでいます" in msg for msg in progress_messages)

    @patch('service.audio_splitter.os.makedirs')
    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    @patch('service.audio_splitter.AudioSegment.from_file')
    @patch('service.audio_splitter._export_chunk')
    def test_split_audio_file_multiple_chunks(
        self,
        mock_export,
        mock_from_file,
        mock_getsize,
        mock_exists,
        mock_makedirs
    ):
        """複数チャンクへの分割"""
        # 100MB のファイルを 24.5MB で分割 -> 5チャンク
        mock_getsize.side_effect = [100 * 1024 * 1024] + [20 * 1024 * 1024] * 5
        mock_exists.return_value = False

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 100000  # 100秒
        mock_audio.__getitem__.return_value = MagicMock()
        mock_from_file.return_value = mock_audio

        result = split_audio_file(
            "test.mp3",
            "output",
            target_chunk_size_mb=24.5,
            output_format="m4a"
        )

        expected_chunks = ceil(100.0 / 24.5)
        assert len(result) == expected_chunks
        assert mock_export.call_count == expected_chunks

    @patch('service.audio_splitter.os.makedirs')
    @patch('service.audio_splitter.os.path.exists')
    @patch('service.audio_splitter.os.path.getsize')
    def test_split_audio_file_no_split_with_callback(
        self,
        mock_getsize,
        mock_exists,
        mock_makedirs
    ):
        """分割不要な場合のコールバック"""
        mock_getsize.return_value = 10 * 1024 * 1024
        mock_exists.return_value = True

        progress_messages = []

        def progress_callback(msg):
            progress_messages.append(msg)

        result = split_audio_file(
            "test.mp3",
            "output",
            target_chunk_size_mb=24.5,
            progress_callback=progress_callback
        )

        assert result == []
        assert any("分割は不要" in msg for msg in progress_messages)
