#!/usr/bin/env python3

import re
from argparse import ArgumentParser
from xml.etree import ElementTree
import requests
import subprocess

def get_meta(video_url, session):
    res = session.get(video_url)
    manifest_url = re.findall(r"src: '(.*manifest.*)'", res.text)[0]

    onelined = re.sub(r"\s+", " ", res.text)
    title = re.findall(r"<div class=\"card-header\">\s*<h3>(.*)</h3>", onelined)[0]

    return {
        "manifest_url": manifest_url,
        "title": title,
    }

def get_segments(manifest_url):
    segment_urls = {}

    # the segments will be downloaded from the same place as the manifest
    base_url = re.match(r"^(.*)manifest\.mpd", manifest_url)[1]

    manifest = requests.get(manifest_url)
    root = ElementTree.fromstring(manifest.text)
    # xml.etree puts the namespace in every tag, retrieve it
    namespace = re.match(r"({.*})MPD", root.tag)[1]

    period = root.find(namespace + "Period")

    for adaption_set in period:
        channel = adaption_set.attrib["mimeType"].split("/")[0]

        repr_id = adaption_set.find(namespace + "Representation").attrib["id"]

        template = adaption_set.find(namespace + "SegmentTemplate")
        media = template.attrib["media"].replace("$RepresentationID$", repr_id)
        init = template.attrib["initialization"].replace("$RepresentationID$", repr_id)

        segment_urls[channel] = [base_url + init]

        time = 0
        timeline = template.find(namespace + "SegmentTimeline")
        for s in timeline:
            segment_urls[channel].append(base_url + media.replace("$Time$", str(time)))

            d = int(s.attrib["d"])
            time += d

        segment_urls[channel].append(base_url + media.replace("$Time$", str(time)))

    return segment_urls

def merge_segments(segment_urls, output_filename):
    print("Download segments")
    for channel, urls in segment_urls.items():
        with open(f"_{channel}.mp4", "wb") as out_file:
            print(channel, ": ", 0, "/", len(urls), sep="", end="", flush=True)
            for i, url in enumerate(urls):
                res = requests.get(url)
                out_file.write(res.content)
                print("\r", channel, ": ", i, "/", len(urls), sep="", end="", flush=True)
            print()

    print("Merge using ffmpeg")
    # TODO: -c copy skips the first 4 seconds of a video, what's going on there?
    subprocess.run(["ffmpeg", "-i", "_audio.mp4", "-i", "_video.mp4", "-c", "copy", output_filename])
    print("Merge complete, you can remove _audio.mp4 and _video.mp4")

if __name__ == "__main__":
    from util import get_authenticated_session, get_credentials

    parser = ArgumentParser(description="""A tool to download videos from the UR Mediathek.
    To use it, you must have a credentials.json file in the current directory which contains the keys 'username' and 'password'.
    """)
    parser.add_argument("url",
                        help="The URL of the site that shows the video. Usually begins with https://mediathek2.uni-regensburg.de/playthis/")
    parser.add_argument("--title", default=None, help="Overwrite the title derived from the mediathek.")

    args = parser.parse_args()

    print("Starting session")
    session = get_authenticated_session(get_credentials())

    meta = get_meta(args.url, session)
    manifest_url = meta["manifest_url"]
    title = meta["title"] if args.title is None else args.title

    seg_urls = get_segments(manifest_url)
    merge_segments(seg_urls, title + ".mp4")
