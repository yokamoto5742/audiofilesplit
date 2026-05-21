# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python 3.13 tkinter GUI application for splitting large audio files into smaller chunks. Supports m4a, mp3, mp4 output formats.

## Setup & Commands

```bash
uv sync                                          # Install dependencies
python main.py                                   # Run GUI
python -m pytest tests/ -v --tb=short           # Run tests
python -m pytest tests/ -v --tb=short --cov=app  # With coverage
pyright                                          # Type check
python -m ruff format .                          # Format code
```

**External requirement:** ffmpeg must be in system PATH. On Windows, download from gyan.dev and add `C:\Program Files\ffmpeg\bin` to PATH. pydub will fail silently without it.

## Architecture

```
main.py               # tkinter root + GUI startup
app/main_window.py    # GUI (3 buttons: split, config, close)
service/audio_splitter.py  # Core logic: split_audio_file() + 3 helpers
utils/config_manager.py    # INI config load/save (utils/config.ini)
```

Config is stored at `utils/config.ini` and managed via `config_manager.py`. When built with PyInstaller, config path resolves via `sys._MEIPASS`.

## Code Conventions

See `.claude/rules/python-coding.md` for full coding standards. Key points:

- Type hints are **mandatory** on all function parameters and return types
- UI-facing strings must be in Japanese and defined as constants — no magic strings inline
- Import order: stdlib → third-party → local (alphabetical within each group, `import` before `from`)
- Functions should stay under 50 lines

## Commit Style

Use emoji + conventional commits:

```
✨ feat(scope): description
🐛 fix(scope): description
♻️ refactor(scope): description
🗑️ chore(scope): description
📝 docs(scope): description
```

## Known Issues

- `build.py` line 15 references undefined `new_version` — do not run it
- `utils/log_rotation.py` exists but is not imported anywhere
