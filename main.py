import os
from pydub import AudioSegment
from math import ceil


def split_audio_if_large(file_path, target_chunk_size_mb=24.5, output_format="m4a"):
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"ファイル: {file_path}, サイズ: {file_size_mb:.2f} MB")

        if file_size_mb <= target_chunk_size_mb:
            print("ファイルサイズが指定された上限以下のため、分割は不要です。")
            return

        print("音声ファイルを読み込んでいます...")
        audio = AudioSegment.from_file(file_path)
        print("読み込み完了。")

        total_duration_ms = len(audio)
        print(f"総再生時間: {total_duration_ms / 1000:.2f} 秒")

        num_chunks = ceil(file_size_mb / target_chunk_size_mb)
        print(f"推定チャンク数: {num_chunks}")

        chunk_duration_ms = ceil(total_duration_ms / num_chunks)
        print(f"各チャンクの目標再生時間: {chunk_duration_ms / 1000:.2f} 秒")

        base_name, ext = os.path.splitext(file_path)

        print("ファイルの分割を開始します...")
        for i in range(num_chunks):
            start_time = i * chunk_duration_ms
            end_time = (i + 1) * chunk_duration_ms
            if end_time > total_duration_ms:
                end_time = total_duration_ms

            if start_time >= total_duration_ms:
                print("すべてのオーディオデータが処理されました。ループを終了します。")
                break

            chunk = audio[start_time:end_time]

            output_filename = f"{base_name}_part{i + 1}.{output_format}"

            print(
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
            print(f"  エクスポート完了: {output_filename}, サイズ: {exported_chunk_size_mb:.2f} MB")

        print("ファイルの分割が完了しました。")

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {file_path}")
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        print("ffmpeg がインストールされ、PATHが通っているか確認してください。")
        print("また、ファイル形式が pydub でサポートされているか確認してください。")


if __name__ == "__main__":

    input_file = r"your_audio_file.m4a"
    target_size_mb = 24.5

    # 出力ファイルのフォーマットを明示的に指定(オプション)
    output_file_format = "m4a"

    if input_file == "your_audio_file.m4a" or not os.path.exists(input_file):
        print("スクリプトを実行する前に、`input_file` 変数を実際の有効なファイルパスに置き換えてください。")
        if input_file != "your_audio_file.m4a":
            print(f"指定されたファイルが見つかりません: {input_file}")
    else:
        split_audio_if_large(input_file, target_chunk_size_mb=target_size_mb, output_format=output_file_format)
