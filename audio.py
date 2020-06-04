#!/usr/bin/env python3

from pathlib import Path
import sys
import requests
from bs4 import BeautifulSoup

# width of the download progress bar
BAR_SIZE = 50

def download_audio(audio_url):
    response = requests.get(audio_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    audio_title = soup.select("h5.card-title")[0].text.strip()
    channel_url = soup.select("a.btn.btn-secondary")[0].get("href")

    channel_id = channel_url.split("/")[-1]

    audio_id = audio_url.split("/")[-1]
    stream_url = f"https://stream5.uni-regensburg.de/audio/grips/{channel_id}/{audio_id}.mp3"

    output_filename = f"{audio_title}.mp3"
    if Path(output_filename).exists():
        print(output_filename, "already exists")
        return

    # https://stackoverflow.com/a/15645088
    print("Downloading", audio_title)
    with open(output_filename, "wb") as f:
        response = requests.get(stream_url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:
            # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(BAR_SIZE * dl / total_length)
                print(f"\r[", '=' * done, ' ' * (BAR_SIZE - done), "]", sep="", end="", flush=True)
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "channel_url")
        exit(1)

    download_audio(sys.argv[1])
