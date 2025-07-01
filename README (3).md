# MP3 Downloader

A desktop app to download MP3 files from YouTube and Spotify playlists. This project uses `yt-dlp` and `spotipy` under the hood, with a friendly GUI built using `tkinter`.

## Features

- Download individual YouTube videos as MP3
- Download all tracks from a Spotify playlist
- Automatically embeds video thumbnails as cover art (YouTube only)
- Clean and customizable file naming
- Remembers your last used download location

## Requirements

- Python 3.9 or later
- A Spotify Developer account (for Spotify playlist support)

## Setup

1. Clone this repository:

```bash
git clone https://github.com/yourusername/mp3-downloader.git
cd mp3-downloader
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Spotify credentials:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

Make sure the redirect URI is also registered in your Spotify Developer Dashboard.

## Usage

- Run `youtube_to_mp3.py` to launch the YouTube downloader.
- Run `spotify_to_mp3.py` to download tracks from a Spotify playlist.

Each script will prompt you for the necessary inputs through a GUI.

## Notes

- The Spotify integration uses a browser login the first time and saves the token locally.
- Your download folder will be remembered between sessions via `config.json`.

