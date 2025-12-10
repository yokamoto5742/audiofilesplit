# 変更履歴

このプロジェクトの変更履歴は[Keep a Changelog](https://keepachangelog.com/ja/1.1.0/)の形式に従っています。
バージョン管理は[セマンティック バージョニング](https://semver.org/lang/ja/)に準拠しています。

## [未リリース]

## [1.0.1] - 2025-12-09

### 追加
- GUI向けの包括的なテストスイートを追加(`tests/test_main_window.py`)
- 音声分割機能向けの包括的なテストスイートを追加(`tests/test_audio_splitter.py`)

### 修正
- ビルドファイルの構成に関する問題を修正

## [1.0.0] - 2025-12-09

### 追加
- 音声ファイル分割機能(コマンドラインおよびGUI版)
- Tkinter ベースのグラフィカルユーザーインターフェース
- 設定ファイル管理システム(`utils/config_manager.py`)
- 音声処理サービスモジュール(`service/audio_splitter.py`)
- Pyright型チェッカー向けのエージェント設定
- pytest テストクリエイター向けのエージェント設定
- プロジェクト構造生成スクリプト

### 変更
- Python の最小バージョン要件を 3.12 に更新
- サンプル入力ファイルのパスを更新

### 依存関係
- pydub を依存関係に追加
- audioop-lts を依存関係に追加

[未リリース]: https://github.com/yokamoto5742/audiofilesplit/compare/v1.0.1...main
[1.0.1]: https://github.com/yokamoto5742/audiofilesplit/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/yokamoto5742/audiofilesplit/releases/tag/v1.0.0
