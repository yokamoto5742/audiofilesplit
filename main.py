import os

from service.audio_splitter import split_audio_file


if __name__ == "__main__":
    input_file = r"C:\Users\yokam\Downloads\2024年度第2回多職種役割分担推進会議241128.m4a"
    target_size_mb = 20
    output_file_format = "m4a"

    if not os.path.exists(input_file):
        print(f"指定されたファイルが見つかりません: {input_file}")
    else:
        # 出力先はファイルと同じディレクトリ
        output_dir = os.path.dirname(input_file)

        # 進捗をコンソールに出力
        def progress(msg):
            print(msg)

        try:
            split_audio_file(
                file_path=input_file,
                output_dir=output_dir,
                target_chunk_size_mb=target_size_mb,
                output_format=output_file_format,
                progress_callback=progress
            )
        except Exception as e:
            print(f"エラー: {e}")
