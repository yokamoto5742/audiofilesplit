import subprocess


def build_executable():
    subprocess.run([
        "pyinstaller",
        "--name=audiofilesplit",
        "--windowed",
        "--icon=assets/audiofilesplit.ico",
        "--add-data", "utils/config.ini:.",
        "main.py"
    ])

    print(f"Executable built successfully.")
    return new_version


if __name__ == "__main__":
    build_executable()
