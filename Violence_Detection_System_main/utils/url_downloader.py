# utils/url_downloader.py

import os
import tempfile
import yt_dlp


def download_video_from_url(url: str) -> str:
    """
    Downloads a video from a URL (YouTube or direct)
    and returns the local file path.
    """

    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "video.%(ext)s")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename
