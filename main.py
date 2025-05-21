import os
from pydub import AudioSegment
from math import ceil


def split_audio_if_large(file_path, target_chunk_size_mb=24.5, output_format="m4a", progress_callback=print):
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        progress_callback(f"ファイル: {file_path}, サイズ: {file_size_mb:.2f} MB")

        if file_size_mb <= target_chunk_size_mb:
            progress_callback("ファイルサイズが指定された上限以下のため、分割は不要です。")
            return

        progress_callback("音声ファイルを読み込んでいます...")
        audio = AudioSegment.from_file(file_path)
        progress_callback("読み込み完了。")

        total_duration_ms = len(audio)
        progress_callback(f"総再生時間: {total_duration_ms / 1000:.2f} 秒")

        num_chunks = ceil(file_size_mb / target_chunk_size_mb)
        progress_callback(f"推定チャンク数: {num_chunks}")

        chunk_duration_ms = ceil(total_duration_ms / num_chunks)
        progress_callback(f"各チャンクの目標再生時間: {chunk_duration_ms / 1000:.2f} 秒")

        base_name, ext = os.path.splitext(file_path)

        progress_callback("ファイルの分割を開始します...")
        for i in range(num_chunks):
            start_time = i * chunk_duration_ms
            end_time = (i + 1) * chunk_duration_ms
            if end_time > total_duration_ms:
                end_time = total_duration_ms

            if start_time >= total_duration_ms:
                progress_callback("すべてのオーディオデータが処理されました。ループを終了します。")
                break

            chunk = audio[start_time:end_time]

            output_filename = f"{base_name}_part{i + 1}.{output_format}"

            progress_callback(
                f"  チャンク {i + 1}/{num_chunks} をエクスポート中: {output_filename} ({start_time / 1000:.2f}s - {end_time / 1000:.2f}s)")

            if output_format.lower() == "m4a":
                export_format_param = "mp4"
                chunk.export(output_filename, format=export_format_param, codec="aac")
            elif output_format.lower() == "mp4":  # MP4 (audio only)
                chunk.export(output_filename, format="mp4", codec="aac")
            elif output_format.lower() == "mp3":
                chunk.export(output_filename, format="mp3")
            else:
                chunk.export(output_filename, format=output_format)

            exported_chunk_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
            progress_callback(f"  エクスポート完了: {output_filename}, サイズ: {exported_chunk_size_mb:.2f} MB")

        progress_callback("ファイルの分割が完了しました。")

    except FileNotFoundError:
        progress_callback(f"エラー: ファイルが見つかりません - {file_path}")
    except Exception as e:
        progress_callback(f"処理中にエラーが発生しました: {e}")
        progress_callback("ffmpeg がインストールされ、PATHが通っているか確認してください。")
        progress_callback("また、ファイル形式が pydub でサポートされているか確認してください。")


if __name__ == "__main__":
    # This part is for command-line execution and testing
    # Replace 'your_audio_file.m4a' with the actual path to your audio file
    # when running directly.
    input_file = r"your_audio_file.m4a"  # Example placeholder
    target_size_mb = 24.5  # Example target size in MB
    output_file_format = "m4a"  # Example output format

    # Check if the placeholder file path is still being used
    if input_file == r"your_audio_file.m4a":
        print("INFO: To run this script directly, please replace the 'input_file' variable")
        print("      in the __main__ block with the path to your audio file.")
        print("      For example: input_file = r'/path/to/your/audio.m4a'")
    elif not os.path.exists(input_file):
        print(f"ERROR: The specified input file does not exist: {input_file}")
    else:
        print(f"Starting audio splitting process for: {input_file}")
        # When run directly, it uses the default 'print' as progress_callback
        split_audio_if_large(
            input_file,
            target_chunk_size_mb=target_size_mb,
            output_format=output_file_format
        )
