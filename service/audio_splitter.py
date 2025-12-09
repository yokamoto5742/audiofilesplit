import os
from math import ceil

from pydub import AudioSegment


def _calculate_chunks(file_size_mb: float, target_chunk_size_mb: float) -> int:
    """チャンク数を計算"""
    return ceil(file_size_mb / target_chunk_size_mb)


def _get_output_filename(file_path: str, output_dir: str, chunk_index: int, output_format: str) -> str:
    """出力ファイル名を生成"""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{base_name}_part{chunk_index + 1}.{output_format}"
    return os.path.join(output_dir, output_filename)


def _export_chunk(chunk: AudioSegment, output_path: str, output_format: str) -> None:
    """音声チャンクをエクスポート"""
    format_lower = output_format.lower()

    if format_lower == "m4a":
        chunk.export(output_path, format="mp4", codec="aac")
    elif format_lower == "mp4":
        chunk.export(output_path, format="mp4", codec="aac")
    elif format_lower == "mp3":
        chunk.export(output_path, format="mp3")
    else:
        chunk.export(output_path, format=output_format)


def split_audio_file(
    file_path: str,
    output_dir: str,
    target_chunk_size_mb: float = 24.5,
    output_format: str = "m4a",
    progress_callback=None
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
        RuntimeError: pydub/ffmpeg関連のエラー
    """
    output_files = []

    try:
        # ファイルサイズチェック
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if progress_callback:
            progress_callback(f"ファイル: {file_path}, サイズ: {file_size_mb:.2f} MB")

        if file_size_mb <= target_chunk_size_mb:
            if progress_callback:
                progress_callback("ファイルサイズが指定された上限以下のため、分割は不要です")
            return output_files

        # 音声ファイル読み込み
        if progress_callback:
            progress_callback("音声ファイルを読み込んでいます...")
        audio = AudioSegment.from_file(file_path)
        if progress_callback:
            progress_callback("読み込み完了")

        # チャンク数と再生時間の計算
        total_duration_ms = len(audio)
        if progress_callback:
            progress_callback(f"総再生時間: {total_duration_ms / 1000:.2f} 秒")

        num_chunks = _calculate_chunks(file_size_mb, target_chunk_size_mb)
        if progress_callback:
            progress_callback(f"推定チャンク数: {num_chunks}")

        chunk_duration_ms = ceil(total_duration_ms / num_chunks)
        if progress_callback:
            progress_callback(f"各チャンクの目標再生時間: {chunk_duration_ms / 1000:.2f} 秒")

        # 出力ディレクトリの確認・作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # ファイル分割処理
        if progress_callback:
            progress_callback("ファイルの分割を開始します...")

        for i in range(num_chunks):
            start_time = i * chunk_duration_ms
            end_time = (i + 1) * chunk_duration_ms
            if end_time > total_duration_ms:
                end_time = total_duration_ms

            if start_time >= total_duration_ms:
                if progress_callback:
                    progress_callback("すべてのオーディオデータが処理されました")
                break

            chunk = audio[start_time:end_time]
            output_path = _get_output_filename(file_path, output_dir, i, output_format)

            if progress_callback:
                progress_callback(
                    f"チャンク {i + 1}/{num_chunks} をエクスポート中: {os.path.basename(output_path)} "
                    f"({start_time / 1000:.2f}s - {end_time / 1000:.2f}s)"
                )

            _export_chunk(chunk, output_path, output_format)

            exported_chunk_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if progress_callback:
                progress_callback(
                    f"エクスポート完了: {os.path.basename(output_path)}, "
                    f"サイズ: {exported_chunk_size_mb:.2f} MB"
                )

            output_files.append(output_path)

        if progress_callback:
            progress_callback("ファイルの分割が完了しました")

        return output_files

    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    except Exception as e:
        error_msg = f"処理中にエラーが発生しました: {e}\n"
        error_msg += "ffmpeg がインストールされ、PATHが通っているか確認してください\n"
        error_msg += "また、ファイル形式が pydub でサポートされているか確認してください"
        raise RuntimeError(error_msg)
