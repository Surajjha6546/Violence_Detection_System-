import yt_dlp
import os

def download_video_from_url(url, output_dir="temp_videos"):
    """
    Downloads a video from a URL (YouTube or direct MP4)
    and returns the local file path.
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)

    return video_path
