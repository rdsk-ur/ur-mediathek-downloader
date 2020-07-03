#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

from util import authenticate, get_credentials

def download_video(video_url, driver, timeout=20, title=None, skip_auth=False):
    if not skip_auth:
        try:
            credentials = get_credentials()
        except:
            return

    driver.get(video_url)

    if not skip_auth:
        authenticate(driver, credentials)

    print("Wait for manifest request")
    try:
        req = driver.wait_for_request("manifest.mpd", timeout)
        manifest_url = req.path
    except TimeoutException:
        print("Did not receive the manifest after", timeout, "seconds")
        print("Are the provided credentials still valid?")
        print("Alternatively, consider increasing the timeout by setting the --timeout option")
        return

    if title is None:
        video_name = driver.find_element_by_css_selector("h5.card-title").text
    else:
        video_name = title

    if manifest_url is None:
        print("Could not find a manifest")
    else:
        print("Video title:", video_name)
        print("Manifest URL:", manifest_url)
        print("Starting youtube-dl")
        os.system(f"youtube-dl -o '{video_name}.mp4' '{manifest_url}'")

if __name__ == "__main__":
    parser = ArgumentParser(description="""A tool to download videos from the UR Mediathek.
    To use it, you must have a credentials.json file in the current directory which contains the keys 'account' and 'password'.
    """)
    parser.add_argument("url", help="The URL of the site that shows the video. Usually begins with https://mediathek2.uni-regensburg.de/playthis/")
    parser.add_argument("--timeout", type=int, default=20, help="The number of seconds that will be waited until the manifest is requested.")
    parser.add_argument("--title", default=None, help="Overwrite the title derived from the mediathek.")

    args = parser.parse_args()

    print("Launch headless firefox")
    options = Options()
    options.headless = True
    with webdriver.Firefox(options=options) as driver:
        download_video(args.url, driver, args.timeout, args.title)
