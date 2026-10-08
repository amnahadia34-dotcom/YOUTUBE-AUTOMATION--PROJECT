import os
import requests
from pathlib import Path
from config.settings import PEXELS_API_KEY

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"


def search_videos(query, per_page=5):
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": per_page
    }

    response = requests.get(
        PEXELS_VIDEO_URL,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def download_video(url, output_path):
    response = requests.get(
        url,
        stream=True,
        timeout=60
    )

    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)

    return output_path


def get_video_for_keyword(keyword, download_dir="downloads"):

    Path(download_dir).mkdir(
        parents=True,
        exist_ok=True
    )

    data = search_videos(keyword)

    videos = data.get("videos", [])

    if not videos:
        return None

    video = videos[0]

    files = video.get("video_files", [])

    if not files:
        return None

    best_file = sorted(
        files,
        key=lambda x: x.get("width", 0),
        reverse=True
    )[0]

    url = best_file["link"]

    filename = f"{keyword.replace(' ', '_')}.mp4"

    output_path = os.path.join(
        download_dir,
        filename
    )

    return download_video(
        url,
        output_path
    )