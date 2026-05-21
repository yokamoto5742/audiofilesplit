import os
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from math import ceil

from service.ffmpeg_runner import (
    _can_stream_copy,
    _probe_audio,
    _split_one_chunk,
)

ProgressCallback = Callable[[str], None]


def _calculate_chunks(file_size_mb: float, target_chunk_size_mb: float) -> int:
    """チャンク数を計算"""
    return ceil(file_size_mb / target_chunk_size_mb)


def _get_output_filename(file_path: str, output_dir: str, chunk_index: int, output_format: str) -> str:
    """出力ファイル名を生成"""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{base_name}_part{chunk_index + 1}.{output_format}"
    return os.path.join(output_dir, output_filename)


def _split_into_chunks(
    file_path: str,
    output_dir: str,
    output_format: str,
    num_chunks: int,
    chunk_duration_s: float,
    stream_copy: bool,
    notify: ProgressCallback,
) -> list[str]:
    """全チャンクを並列に切り出す"""
    output_files: list[str] = [""] * num_chunks
    completed = 0
    lock = threading.Lock()

    def run_chunk(index: int) -> None:
        nonlocal completed
        start_s = index * chunk_duration_s
        output_path = _get_output_filename(file_path, output_dir, index, output_format)
        _split_one_chunk(file_path, output_path, start_s, chunk_duration_s, output_format, stream_copy)
        output_files[index] = output_path
        with lock:
            completed += 1
            notify(f"チャンク {completed}/{num_chunks} を出力しました")

    max_workers = min(num_chunks, os.cpu_count() or 1)
    notify(f"ファイルの分割を開始します (並列数: {max_workers})")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_chunk, i) for i in range(num_chunks)]
        for future in futures:
            future.result()

    return output_files


def split_audio_file(
    file_path: str,
    output_dir: str,
    target_chunk_size_mb: float = 24.5,
    output_format: str = "m4a",
    progress_callback: ProgressCallback | None = None,
) -> list[str]:
    """
    音声ファイルを指定サイズで分割

    Args:
        file_path: 入力ファイルパス
        output_dir: 出力ディレクトリ
        target_chunk_size_mb: 目標チャンクサイズ(MB)
        output_format: 出力フォーマット (m4a, mp3, mp4等)
        progress_callback: 進捗コールバック関数 callback(message: str)

    Returns:
        生成されたファイルパスのリスト

    Raises:
        FileNotFoundError: 入力ファイルが存在しない
        RuntimeError: ffmpeg/ffprobe 関連のエラー
    """
    def notify(message: str) -> None:
        if progress_callback:
            progress_callback(message)

    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    notify(f"ファイル: {file_path}, サイズ: {file_size_mb:.2f} MB")

    if file_size_mb <= target_chunk_size_mb:
        notify("ファイルサイズが指定された上限以下のため、分割は不要です")
        return []

    try:
        notify("音声情報を解析しています...")
        duration_s, input_codec = _probe_audio(file_path)
        notify(f"総再生時間: {duration_s:.2f} 秒")

        num_chunks = _calculate_chunks(file_size_mb, target_chunk_size_mb)
        chunk_duration_s = duration_s / num_chunks
        notify(f"推定チャンク数: {num_chunks}")

        os.makedirs(output_dir, exist_ok=True)

        stream_copy = _can_stream_copy(input_codec, output_format)
        if stream_copy:
            notify("コーデックが一致するため、再エンコードせずに分割します")
        else:
            notify("再エンコードしながら分割します")

        output_files = _split_into_chunks(
            file_path, output_dir, output_format,
            num_chunks, chunk_duration_s, stream_copy, notify,
        )
        notify("ファイルの分割が完了しました")
        return output_files

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"処理中にエラーが発生しました: {e}")
