#!/usr/bin/env python3

import os
import re
from argparse import ArgumentParser

# width of the download progress bar
BAR_SIZE = 50


def download_audio(audio_url, session, title=None):
    res = session.get(audio_url)
    onelined = re.sub(r"\s+", " ", res.text)

    if not title:
        title = re.findall(r"<div class=\"card-header\">\s*<h3>(.*)</h3>", onelined)[0]

    channel_id = re.findall(r"https://mediathek2\.uni-regensburg\.de/list/(\d+)", onelined)[0]
    audio_id = audio_url.split("/")[-1]

    stream_url = f"https://stream5.uni-regensburg.de/audio/grips/{channel_id}/{audio_id}.mp3"
    print(stream_url)

    output_filename = f"{title}.mp3"
    if os.path.exists(output_filename):
        print(output_filename, "already exists")
        return

    # https://stackoverflow.com/a/15645088
    print("Downloading", title)
    with open(output_filename, "wb") as f:
        res = session.get(stream_url, stream=True)
        total_length = res.headers.get('content-length')

        if total_length is None:
            # no content length header
            f.write(res.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in res.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(BAR_SIZE * dl / total_length)
                print(f"\r[", '=' * done, ' ' * (BAR_SIZE - done), "]", sep="", end="", flush=True)
    print()


if __name__ == "__main__":
    from util import get_authenticated_session, get_credentials

    parser = ArgumentParser(description="""A tool to download audio from the UR Mediathek.
    To use it, you must have a credentials.json file in the current directory which contains the keys 'account' and 'password'.
    """)
    parser.add_argument("url",
                        help="The URL of the site that shows the audio. Usually begins with https://mediathek2.uni-regensburg.de/playthis/")
    parser.add_argument("--title", default=None, help="Overwrite the title derived from the mediathek.")

    args = parser.parse_args()

    print("Starting session")
    session = get_authenticated_session(get_credentials())
    download_audio(args.url, session, args.title)
