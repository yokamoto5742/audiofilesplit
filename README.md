# 音声ファイル分割ツール AudioFileSplit

大きな音声ファイルを指定したサイズに基づいて小さなチャンクに分割するPythonツール。GUIとCLIの両方をサポートし、複数の出力形式に対応しています。

## 主な機能

- 音声ファイルの自動分割（目標ファイルサイズ指定）
- 複数の出力形式をサポート（m4a、mp3、mp4）
- 分割処理の詳細なログ出力

## 前提条件

### 必須
- **Python 3.13 以上**
- **ffmpeg**: システムのPATHに追加されていることが必要

### ffmpegのインストール（Windows）

1. [gyan.dev (FFmpeg builds)](https://www.gyan.dev/ffmpeg/builds/) にアクセス
2. `ffmpeg-release-essentials.zip` をダウンロード
3. ZIPファイルを解凍してbinフォルダの中身をProgram Filesに保存（例：`C:\Program Files\ffmpeg`）
4. Windows環境変数のPATHに `C:\Program Files\ffmpeg\bin` を追加

インストール確認：
```bash
ffmpeg -version
```

## インストール手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/yokamoto5742/audiofilesplit.git
cd audiofilesplit
```

### 2. 仮想環境の作成と依存パッケージのインストール

事前に [uv](https://docs.astral.sh/uv/getting-started/installation/) のインストールが必要です。

```bash
# 仮想環境の作成とパッケージのインストールを一度に行う
uv sync
```

仮想環境を有効化する：

```bash
# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

## 使用方法

```bash
python main.py
```

GUIウィンドウが起動します。以下の操作が可能です：

- **音声ファイル分割**: ファイル選択ダイアログから音声ファイルを選択し、分割処理を実行
- **設定ファイル**: `config.ini` をメモ帳で開いて分割設定やパスを変更

## 主要コンポーネント

### 音声分割エンジン（service/audio_splitter.py）

**split_audio_file()** - メイン関数

```python
from service.audio_splitter import split_audio_file

output_files = split_audio_file(
    file_path="path/to/audio.m4a",
    output_dir="output/directory",
    target_chunk_size_mb=20.0,
    output_format="m4a",
    progress_callback=lambda msg: print(msg)
)
```

**パラメータ:**
- `file_path` (str): 入力ファイルパス
- `output_dir` (str): 出力ディレクトリ
- `target_chunk_size_mb` (float): 目標チャンクサイズ（MB）、デフォルト: 24.5
- `output_format` (str): 出力形式（m4a/mp3/mp4等）、デフォルト: m4a
- `progress_callback` (function): 進捗メッセージ用コールバック関数（オプション）

**戻り値:**
- 生成されたファイルパスのリスト

**例外:**
- `FileNotFoundError`: 入力ファイルが存在しない場合
- `RuntimeError`: ffmpeg/pydub関連エラー

### 設定管理（utils/config_manager.py）

設定ファイル（`utils/config.ini`）の読み込みと保存を管理します。

```python
from utils.config_manager import load_config

config = load_config()
target_mb = config.getint('Audio', 'target_size_mb')
output_format = config.get('Audio', 'output_file_format')
```

**設定セクション:**

```ini
[Appearance]
window_width = 280
window_height = 200
font_size = 11

[Paths]
downloads_path = C:\Users\yokam\Downloads
output_path = C:\Shinseikai\audiofilesplit\output

[Audio]
target_size_mb = 20
output_file_format = m4a
```

## 開発環境セットアップ

### テスト実行
```bash
# すべてのテストを実行
python -m pytest tests/ -v --tb=short

# 特定のテストファイルを実行
python -m pytest tests/test_audio_splitter.py -v

# カバレッジレポート付き
python -m pytest tests/ -v --cov=app --cov=service --cov=utils
```

### 型チェック
```bash
# pyrightで型チェック実行
pyright
```

### ビルド（実行ファイル生成）
```bash
# PyInstallerで実行ファイルを生成（バージョン自動インクリメント）
python build.py
```

## トラブルシューティング

### ffmpegが見つからないエラー
```
エラー: ffmpeg がインストールされ、PATHが通っているか確認してください
```
**解決方法:**
- ffmpegがインストールされているか確認
- システムのPATH環境変数に ffmpeg/bin のパスが含まれているか確認
- PyCharmやターミナルを再起動してPATH変更を反映

### 音声ファイル形式がサポートされていないエラー
```
エラー: ファイル形式が pydub でサポートされているか確認してください
```
**解決方法:**
- 対応形式: WAV、MP3、M4A、FLAC、AAC、OGG、WMA、MP4
- 別の形式に変換してから試す

### 分割処理中にエラーが発生
```
エラー: 処理中にエラーが発生しました
```
**解決方法:**
- ファイルが破損していないか確認
- ffmpegのバージョンを最新に更新
- ディスク容量が十分か確認

## ライセンス

このプロジェクトのライセンス情報については、 [LICENSE](docs/LICENSE) を参照してください。

## 更新履歴

更新履歴は [CHANGELOG.md](docs/CHANGELOG.md) を参照してください。
