import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from downloader import download_track_with_metadata  # Moved logic here

# ---------- GUI SETUP ----------
root = tk.Tk()
root.title("YouTube to MP3 Downloader (yt-dlp)")
root.geometry("650x370")
root.configure(bg="#1e1e1e")

# Bring to front (macOS fix)
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)

# ---------- THEME SETUP ----------
style = ttk.Style()
style.theme_use("default")
style.configure("TButton", font=("Segoe UI", 10), padding=6, background="#4CAF50", foreground="white")
style.map("TButton", background=[("active", "#45a049")], foreground=[("active", "white")])

entry_style = {"bg": "#2b2b2b", "fg": "white", "insertbackground": "white"}

# ---------- GUI FUNCTIONS ----------
def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)

def update_status(message, color="white"):
    status_label.config(text=message, fg=color)

def autofill_filename(*args):
    url = url_entry.get().strip()
    if not url:
        return
    try:
        from yt_dlp import YoutubeDL
        options = {'noplaylist': not playlist_var.get()}
        ydl = YoutubeDL(options)
        info = ydl.extract_info(url, download=False)
        filename_entry.delete(0, tk.END)
        filename_entry.insert(0, info.get('title', ''))
    except Exception:
        update_status("⚠️ Couldn't fetch title", "orange")

def download_audio():
    threading.Thread(target=_download_worker).start()

def _download_worker():
    url = url_entry.get().strip()
    folder = folder_var.get().strip()
    custom_name = filename_entry.get().strip()
    download_playlist = playlist_var.get()

    if not url or not folder:
        messagebox.showerror("Missing Info", "Please provide a YouTube URL and select a folder.")
        return

    update_status("Working...", "blue")

    try:
        result = download_track_with_metadata(
            url=url,
            output_dir=folder,
            filename=custom_name or None,
            embed_thumbnail=not download_playlist
        )
        update_status(f"✅ Saved: {os.path.basename(result)}", "green")
    except Exception as e:
        update_status("❌ Download failed", "red")
        messagebox.showerror("Error", str(e))

# ---------- GUI LAYOUT ----------
tk.Label(root, text="YouTube URL:", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10, pady=(12, 0))
url_entry = tk.Entry(root, width=75, **entry_style)
url_entry.pack(padx=10, pady=(0, 12))
url_entry.bind("<FocusOut>", autofill_filename)

tk.Label(root, text="Custom Filename (optional):", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10)
filename_entry = tk.Entry(root, width=75, **entry_style)
filename_entry.pack(padx=10, pady=(0, 12))

tk.Label(root, text="Save Folder:", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10)
folder_frame = tk.Frame(root, bg="#1e1e1e")
folder_frame.pack(padx=10, pady=(0, 12), fill="x")

folder_var = tk.StringVar()
folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=60, **entry_style)
folder_entry.pack(side="left", expand=True, fill="x")
ttkt = ttk.Button(folder_frame, text="Browse", command=select_folder)
ttkt.pack(side="left", padx=(5, 0), ipadx=10)

# Playlist checkbox
playlist_var = tk.BooleanVar()
playlist_check = tk.Checkbutton(root, text="Download entire playlist", variable=playlist_var,
                                bg="#1e1e1e", fg="white", activebackground="#1e1e1e",
                                activeforeground="white", selectcolor="#1e1e1e")
playlist_check.pack(anchor="w", padx=10, pady=(0, 10))

ttk.Button(root, text="Download MP3", command=download_audio).pack(pady=12, ipadx=20, ipady=8)

status_label = tk.Label(root, text="", fg="white", bg="#1e1e1e")
status_label.pack()

root.mainloop()
