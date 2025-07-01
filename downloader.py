import os
import requests
import yt_dlp
from mutagen.id3 import ID3, error
from mutagen.id3._frames import APIC
from mutagen.mp3 import MP3
from typing import Optional

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in " -_").rstrip()

def download_track_with_metadata(url: str, output_dir: str, filename: Optional[str] = None, embed_thumbnail: bool = True) -> str:
    """
    Downloads an MP3 from a YouTube URL, optionally embedding the thumbnail.

    Args:
        url (str): YouTube video URL
        output_dir (str): Folder path to save the MP3
        filename (str, optional): Custom filename (without extension)
        embed_thumbnail (bool): Whether to embed the thumbnail as cover art

    Returns:
        str: Path to the saved MP3 file
    """
    os.makedirs(output_dir, exist_ok=True)

    # Fetch metadata first
    with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title')
        thumbnail_url = info.get('thumbnail')

    safe_name = sanitize_filename(filename or title)
    outtmpl = os.path.join(output_dir, f"{safe_name}.%(ext)s")
    mp3_path = os.path.join(output_dir, f"{safe_name}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if embed_thumbnail and thumbnail_url:
        try:
            response = requests.get(thumbnail_url)
            response.raise_for_status()
            audio = MP3(mp3_path, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=response.content
                )
            )
            audio.save()
        except Exception as e:
            print("[!] Failed to embed thumbnail:", e)

    return mp3_path
