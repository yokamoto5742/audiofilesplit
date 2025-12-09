# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## House Rules:
- 文章ではなくパッチの差分を返す。
- コードの変更範囲は最小限に抑える。
- コードの修正は直接適用する。
- Pythonのコーディング規約はPEP8に従います。
- KISSの原則に従い、できるだけシンプルなコードにします。
- 可読性を優先します。一度読んだだけで理解できるコードが最高のコードです。
- Pythonのコードのimport文は以下の適切な順序に並べ替えてください。
標準ライブラリ
サードパーティライブラリ
カスタムモジュール 
それぞれアルファベット順に並べます。importが先でfromは後です。

## CHANGELOG
このプロジェクトにおけるすべての重要な変更は日本語でdcos/CHANGELOG.mdに記録します。
フォーマットは[Keep a Changelog](https://keepachangelog.com/ja/1.1.0/)に基づきます。

## Automatic Notifications (Hooks)
自動通知は`.claude/settings.local.json` で設定済：
- **Stop Hook**: ユーザーがClaude Codeを停止した時に「作業が完了しました」と通知
- **SessionEnd Hook**: セッション終了時に「Claude Code セッションが終了しました」と通知

## クリーンコードガイドライン
- 関数のサイズ：関数は50行以下に抑えることを目標にしてください。関数の処理が多すぎる場合は、より小さなヘルパー関数に分割してください。
- 単一責任：各関数とモジュールには明確な目的が1つあるようにします。無関係なロジックをまとめないでください。
- 命名：説明的な名前を使用してください。`tmp` 、`data`、`handleStuff`のような一般的な名前は避けてください。例えば、`doCalc`よりも`calculateInvoiceTotal` の方が適しています。
- DRY原則：コードを重複させないでください。類似のロジックが2箇所に存在する場合は、共有関数にリファクタリングしてください。それぞれに独自の実装が必要な場合はその理由を明確にしてください。
- コメント:分かりにくいロジックについては説明を加えます。説明不要のコードには過剰なコメントはつけないでください。
- コメントとdocstringは必要最小限に日本語で記述します。文末に"。"や"."をつけないでください。

## Project Overview

Audio file splitter tool that divides large audio files into smaller chunks based on target file size. Features a GUI (Tkinter) and uses pydub/ffmpeg for audio processing.

## Key Requirements

- Python 3.12+
- ffmpeg must be installed and in system PATH
- Dependencies: pydub, audioop-lts, uv (see requirements.txt)

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run main script (CLI version)
python main.py

# Run GUI application
python -m app.main_window

# Run project structure generator
python scripts/project_structure.py
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run specific test file
python -m pytest tests/path/to/test_file.py -v
```

### Type Checking
```bash
# Run pyright type checker (configured in pyrightconfig.json)
pyright
```

### Building
```bash
# Build executable with PyInstaller (auto-increments version)
python build.py
```

## Architecture

### Directory Structure
- `app/`: GUI application (Tkinter)
  - `main_window.py`: Main window class
  - `__init__.py`: Version info (__version__, __date__)
- `service/`: Business logic services (currently empty placeholder)
- `utils/`: Utility modules
  - `config_manager.py`: Config file (config.ini) loader/saver
- `scripts/`: Development tools
  - `version_manager.py`: Version increment and README update
  - `project_structure.py`: Project tree generator
- `main.py`: Core audio splitting logic (CLI version)
- `build.py`: PyInstaller build script with version management

### Key Components

**Audio Splitting Logic** (main.py):
- `split_audio_if_large()`: Main function that reads audio, calculates chunks based on target MB, exports segments
- Supports m4a, mp3, mp4 output formats
- Uses pydub.AudioSegment with ffmpeg backend

**Configuration** (utils/config_manager.py):
- Loads config.ini for appearance settings and paths
- Handles both PyInstaller frozen and regular Python execution
- Config sections: [Appearance] (font_size, window dimensions), [Paths] (downloads_path, output_path)

**Version Management** (scripts/version_manager.py):
- Reads/updates version in app/__init__.py
- Updates README.md with version and date
- `increment_version()`: Increments patch version (X.Y.Z+1)
- `update_version()`: Full update workflow

**Type Checking** (pyrightconfig.json):
- Standard mode, Python 3.12
- Includes: app, service, utils
- Excludes: tests, scripts

## Development Notes

- Japanese comments are used throughout codebase for clarity on logic
- Config file (config.ini) is bundled with PyInstaller builds
- Version format: semantic versioning (major.minor.patch)
- build.py auto-increments version before creating executable
- GUI uses Yu Gothic UI font for Japanese text display
