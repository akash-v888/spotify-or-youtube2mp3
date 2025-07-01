import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from downloader import download_track_with_metadata

import yt_dlp

import json

load_dotenv()
assert os.getenv("SPOTIPY_CLIENT_ID"), "SPOTIPY_CLIENT_ID is missing"
assert os.getenv("SPOTIPY_CLIENT_SECRET"), "SPOTIPY_CLIENT_SECRET is missing"
assert os.getenv("SPOTIPY_REDIRECT_URI"), "SPOTIPY_REDIRECT_URI is missing"

CONFIG_PATH = "config.json"
DEFAULT_FOLDER = os.path.expanduser("~/Downloads")


# ---------- SPOTIFY AUTH ----------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private",
    cache_path=".spotify_token_cache",
    open_browser=True,
    show_dialog=False
))

# ---------- PATH SETUP -----------
def save_last_path(path: str):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"last_folder": path}, f)
    except Exception as e:
        print("Could not save folder path:", e)

def load_last_path() -> str:
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("last_folder", DEFAULT_FOLDER)
    except Exception:
        return DEFAULT_FOLDER

# ---------- GUI SETUP ----------
root = tk.Tk()
root.title("Spotify Playlist to MP3")
root.geometry("650x400")
root.configure(bg="#1e1e1e")

# Bring to front (macOS fix)
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)

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
        save_last_path(folder_selected)

def update_status(message, color="white"):
    status_label.config(text=message, fg=color)
    status_label.update_idletasks()

def download_playlist():
    threading.Thread(target=_download_worker).start()

def _download_worker():
    url = url_entry.get().strip()
    folder = folder_var.get().strip()

    if not url or not folder:
        messagebox.showerror("Missing Info", "Please provide a Spotify Playlist URL and folder.")
        return

    update_status("Fetching playlist...", "blue")
    try:
        playlist_id = url.split("playlist/")[-1].split("?")[0]
        results = sp.playlist_tracks(playlist_id)
        if not results or 'items' not in results:
            raise Exception("No playlist items found")
        tracks = results['items']
    except Exception as e:
        update_status("❌ Failed to fetch playlist", "red")
        messagebox.showerror("Error", str(e))
        return

    progress_bar["maximum"] = len(tracks)
    progress_bar["value"] = 0

    for i, item in enumerate(tracks):
        track = item['track']
        name = track['name']
        artist = track['artists'][0]['name']
        search_query = f"{name} {artist} audio"

        update_status(f"Searching: {name} - {artist}", "white")

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                if not info or 'entries' not in info or not info['entries']:
                    raise Exception(f"No YouTube results for: {search_query}")
                yt_url = info['entries'][0]['webpage_url']

                download_track_with_metadata(
                    url=yt_url,
                    output_dir=folder,
                    filename=f"{name} - {artist}"
                )
        except Exception as e:
            print(f"[!] Failed to download {name}: {e}")
            continue

        progress_bar["value"] = i + 1
        progress_bar.update()

    update_status("✅ Playlist Download Complete!", "green")

# ---------- GUI LAYOUT ----------
tk.Label(root, text="Spotify Playlist URL:", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10, pady=(12, 0))
url_entry = tk.Entry(root, width=75, **entry_style)
url_entry.pack(padx=10, pady=(0, 12))

tk.Label(root, text="Save Folder:", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10)
folder_frame = tk.Frame(root, bg="#1e1e1e")
folder_frame.pack(padx=10, pady=(0, 12), fill="x")

folder_var = tk.StringVar(value=load_last_path())
folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=60, **entry_style)
folder_entry.pack(side="left", expand=True, fill="x")
ttk.Button(folder_frame, text="Browse", command=select_folder).pack(side="left", padx=(5, 0), ipadx=10)

ttk.Button(root, text="Download Playlist", command=download_playlist).pack(pady=10, ipadx=20, ipady=6)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=580, mode="determinate")
progress_bar.pack(pady=(5, 10), padx=10)

status_label = tk.Label(root, text="", fg="white", bg="#1e1e1e")
status_label.pack()

root.mainloop()
