#!/usr/bin/env python3

import re
import subprocess
from argparse import ArgumentParser


def download_video(video_url, session, title=None):
    res = session.get(video_url)
    manifest_url = re.findall(r"src: '(.*manifest.*)'", res.text)[0]

    if not title:
        onelined = re.sub(r"\s+", " ", res.text)
        title = re.findall(r"<div class=\"card-header\">\s*<h3>(.*)</h3>", onelined)[0]

    print("Video title:", title)
    print("Manifest URL:", manifest_url)
    print("Starting youtube-dl")
    subprocess.run(["youtube-dl", "-o", f"{title}.mp4", manifest_url])


if __name__ == "__main__":
    from util import get_authenticated_session, get_credentials

    parser = ArgumentParser(description="""A tool to download videos from the UR Mediathek.
    To use it, you must have a credentials.json file in the current directory which contains the keys 'account' and 'password'.
    """)
    parser.add_argument("url",
                        help="The URL of the site that shows the video. Usually begins with https://mediathek2.uni-regensburg.de/playthis/")
    parser.add_argument("--title", default=None, help="Overwrite the title derived from the mediathek.")

    args = parser.parse_args()

    print("Starting session")
    session = get_authenticated_session(get_credentials())
    download_video(args.url, session, args.title)
