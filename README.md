# Audio File Splitter

This tool allows you to split large audio files into smaller chunks based on a target file size. It provides a graphical user interface (GUI) for easy operation.

## Features

-   Select an audio file through a file dialog.
-   Specify a target chunk size in megabytes (MB).
-   Choose an output format (m4a, mp3, mp4).
-   View progress and error messages during the splitting process.

## Prerequisites

-   Python 3.x
-   ffmpeg: This application relies on `ffmpeg` for audio processing. Ensure `ffmpeg` is installed and accessible in your system's PATH. You can download it from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).
-   The Python libraries listed in `requirements.txt`.

## How to Run

1.  **Clone the repository or download the files.**
2.  **Install dependencies:**
    Open a terminal or command prompt in the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the GUI application:**
    ```bash
    python gui.py
    ```
4.  **Using the Application:**
    *   Click "Select Audio File" to choose your audio file.
    *   Enter the desired "Target chunk size (MB)".
    *   Select the "Output format".
    *   Click "Split Audio".
    *   The split files will be saved in the same directory as the original file, with "_partX" appended to their names.

## Notes

-   The application uses the `pydub` library for audio manipulation, which in turn requires `ffmpeg`.
-   Supported input formats depend on your `ffmpeg` installation. Common formats like WAV, MP3, M4A, FLAC should work.
