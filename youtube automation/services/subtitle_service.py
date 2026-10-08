import os
import re
from datetime import timedelta


def _seconds_to_timestamp(seconds: float) -> str:
    td = timedelta(seconds=round(seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},000"


def build_subtitles(script: str, language: str = "English") -> list[dict]:
    text = re.sub(r"\s+", " ", script.strip())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if not sentences:
        sentences = [text]

    subtitles = []
    start_time = 0.0

    for index, sentence in enumerate(sentences, start=1):
        duration = max(4.0, min(8.0, len(sentence) / 15.0))
        end_time = start_time + duration

        subtitles.append({
            "index": index,
            "start": _seconds_to_timestamp(start_time),
            "end": _seconds_to_timestamp(end_time),
            "text": sentence.strip()
        })

        start_time = end_time + 0.2

    return subtitles


def write_subtitles_srt(subtitles: list[dict], destination: str) -> str:
    os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
    with open(destination, "w", encoding="utf-8") as file:
        for item in subtitles:
            file.write(f"{item['index']}\n")
            file.write(f"{item['start']} --> {item['end']}\n")
            file.write(f"{item['text']}\n\n")
    return destination
