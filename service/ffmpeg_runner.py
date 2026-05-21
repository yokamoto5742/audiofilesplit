import subprocess

# 出力フォーマットごとの音声コーデック名(ストリームコピー可否の判定に使用)
_COPY_CODEC_MAP = {"m4a": "aac", "mp4": "aac", "mp3": "mp3"}

# 出力フォーマットごとの再エンコード用エンコーダ
_ENCODER_MAP = {"m4a": "aac", "mp4": "aac", "mp3": "libmp3lame"}


def _run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """ffmpeg/ffprobe コマンドを実行(コンソールウィンドウは非表示)"""
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"{cmd[0]} が見つかりません。ffmpeg をインストールし、PATH を通してください"
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        raise RuntimeError(f"{cmd[0]} の実行に失敗しました: {stderr[-500:]}")


def _probe_audio(file_path: str) -> tuple[float, str]:
    """ffprobe で音声の再生時間(秒)とコーデック名を取得"""
    result = _run_command([
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name:format=duration",
        "-of", "default=noprint_wrappers=1:nokey=0",
        file_path,
    ])

    info: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            info[key.strip()] = value.strip()

    try:
        duration = float(info.get("duration", ""))
    except ValueError:
        raise RuntimeError("音声の再生時間を取得できませんでした")

    if duration <= 0:
        raise RuntimeError("音声の再生時間を取得できませんでした")

    return duration, info.get("codec_name", "")


def _can_stream_copy(input_codec: str, output_format: str) -> bool:
    """入力コーデックと出力フォーマットが一致し、再エンコード不要かを判定"""
    expected = _COPY_CODEC_MAP.get(output_format.lower())
    return expected is not None and input_codec.lower() == expected


def _split_one_chunk(
    file_path: str,
    output_path: str,
    start_s: float,
    duration_s: float,
    output_format: str,
    stream_copy: bool,
) -> None:
    """1チャンクを ffmpeg で切り出す(-ss を -i の前に置き高速シーク)"""
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_s:.3f}",
        "-i", file_path,
        "-t", f"{duration_s:.3f}",
        "-map", "0:a:0",
    ]

    if stream_copy:
        cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
    else:
        codec = _ENCODER_MAP.get(output_format.lower())
        if codec:
            cmd += ["-c:a", codec]

    cmd.append(output_path)
    _run_command(cmd)
