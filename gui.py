import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from main import split_audio_if_large

selected_filepath_var = tk.StringVar()
selected_filepath_var.set("Selected file: None")

def log_message(message):

    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)
    log_area.config(state=tk.DISABLED)

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=(("Audio Files", "*.m4a *.mp3 *.mp4 *.wav *.aac *.flac"),
                   ("All files", "*.*"))
    )
    if filepath:
        selected_filepath_var.set(f"Selected file: {filepath}")
        log_message(f"Selected audio file: {filepath}")
    else:
        log_message("File selection cancelled.")


def start_split():
    filepath_full = selected_filepath_var.get()
    prefix = "Selected file: "

    if not filepath_full.startswith(prefix) or filepath_full == prefix + "None":
        log_message("Error: No file selected. Please select a file first.")
        return
    
    filepath = filepath_full[len(prefix):]

    chunk_size_str = chunk_size_var.get()
    try:
        chunk_size_float = float(chunk_size_str)
        if chunk_size_float <= 0:
            log_message("Error: Chunk size must be a positive number.")
            return
    except ValueError:
        log_message(f"Error: Invalid chunk size '{chunk_size_str}'. Please enter a number (e.g., 24.5).")
        return

    output_format = output_format_var.get()

    log_area.config(state=tk.NORMAL)
    log_area.delete('1.0', tk.END)

    log_message(f"Starting audio split for {filepath}...")
    log_message(f"Target chunk size: {chunk_size_float} MB, Output format: {output_format}")

    try:
        split_audio_if_large(
            file_path=filepath,
            target_chunk_size_mb=chunk_size_float,
            output_format=output_format,
            progress_callback=log_message
        )
        log_message("Splitting process completed successfully.")
    except FileNotFoundError: # Specific exception from split_audio_if_large
        log_message(f"Error: The file {filepath} was not found by the splitting function.")
    except Exception as e:
        log_message(f"An unexpected error occurred during splitting: {e}")
        # For debugging, you might want to print the full traceback to console
        import traceback
        print(f"Error during splitting: {e}\n{traceback.format_exc()}")
    finally:
        log_message("Splitting process finished (or an error occurred).")


root = tk.Tk()
root.title("AudioSplitter")

select_button = ttk.Button(root, text="Select Audio File", command=select_file)
select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

selected_file_label = ttk.Label(root, textvariable=selected_filepath_var)
selected_file_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")

chunk_size_label = ttk.Label(root, text="Target chunk size (MB):")
chunk_size_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

chunk_size_var = tk.StringVar(value="24.5")
chunk_size_entry = ttk.Entry(root, textvariable=chunk_size_var)
chunk_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

output_format_label = ttk.Label(root, text="Output format:")
output_format_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

output_format_var = tk.StringVar(value="m4a")
output_format_combobox = ttk.Combobox(root, textvariable=output_format_var, values=["m4a", "mp3", "mp4", "wav", "aac", "flac"], state="readonly")
output_format_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

split_button = ttk.Button(root, text="Split Audio", command=start_split)
split_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

log_area = scrolledtext.ScrolledText(root, width=60, height=10, wrap=tk.WORD, state=tk.DISABLED)
log_area.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")


root.columnconfigure(1, weight=1)

log_message("Audio Splitter GUI started. Select a file and click 'Split Audio'.")

root.mainloop()
