#!/usr/bin/env python3

import os
import sys
import json
from argparse import ArgumentParser
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

def main(video_url, timeout=20):
    credentials_path = os.path.dirname(__file__) + "/credentials.json"
    try:
        with open(credentials_path) as credentials_file:
            credentials = json.load(credentials_file)
    except FileNotFoundError:
        print(credentials_path, "is missing. Please read the readme for more details")
        return
    except json.decoder.JSONDecodeError:
        print("credentials.json is no valid JSON file")
        return

    print("Launch headless browser")
    options = Options()
    options.headless = True
    with webdriver.Firefox(options=options) as driver:
        driver.get(sys.argv[1])

        print("Enter credentials")
        acount_name = credentials["account"]
        password = credentials["password"]
        driver.execute_script(f"document.querySelector('#frmLoginRzaccout').value='{acount_name}'")
        driver.execute_script(f"document.querySelector('#frmLoginPassword').value='{password}'")
        driver.execute_script('document.querySelector("form.form-signin button").click()')

        print("Wait for manifest request")
        try:
            req = driver.wait_for_request("manifest.mpd", timeout)
            manifest_url = req.path
        except TimeoutException:
            print("Did not receive the manifest after", timeout, "seconds")
            print("Consider increasing the timeout by setting the --timeout option")
            return

        video_name = driver.find_element_by_css_selector("h5.card-title").text

    if manifest_url is None:
        print("Could not find a manifest")
    else:
        print("Video title:", video_name)
        print("Manifest URL:", manifest_url)
        print("Starting youtube-dl")
        os.system(f"youtube-dl '{manifest_url}'")

if __name__ == "__main__":
    parser = ArgumentParser(description="""A tool to download videos from the UR Mediathek.
    To use it, you must have a credentials.json file in the current directory which contains the keys 'account' and 'password'.
    """)
    parser.add_argument("url", help="The URL of the site that shows the video. Usually begins with https://mediathek2.uni-regensburg.de/playthis/")
    parser.add_argument("--timeout", default=20, help="The number of seconds that will be waited until the manifest is requested.")

    args = parser.parse_args()
    main(args.url, args.timeout)
