#!/usr/bin/env python3

from pathlib import Path
import sys
from argparse import ArgumentParser
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from util import authenticate, get_credentials

# width of the download progress bar
BAR_SIZE = 50

def download_audio(audio_url, driver, title=None, is_authenticated=False):
    if not is_authenticated:
        try:
            credentials = get_credentials()
        except:
            return

    driver.get(audio_url)

    if not is_authenticated:
        authenticate(driver, credentials)

        wait = WebDriverWait(driver, 10)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, ".card-header h3")))

    if title is None:
        audio_title = driver.find_element_by_css_selector("h4[dusk='asset_title']").text.strip()
    else:
        audio_title = title

    channel_url = driver.find_element_by_css_selector("a.btn.btn-primary").get_attribute("href")

    channel_id = channel_url.split("/")[-1]

    audio_id = audio_url.split("/")[-1]
    stream_url = f"https://stream5.uni-regensburg.de/audio/grips/{channel_id}/{audio_id}.mp3"
    print(stream_url)

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
    parser = ArgumentParser(description="""A tool to download audio from the UR Mediathek.
    To use it, you must have a credentials.json file in the current directory which contains the keys 'account' and 'password'.
    """)
    parser.add_argument("url", help="The URL of the site that shows the audio. Usually begins with https://mediathek2.uni-regensburg.de/playthis/")
    parser.add_argument("--title", default=None, help="Overwrite the title derived from the mediathek.")

    args = parser.parse_args()

    options = Options()
    options.headless = True
    with webdriver.Firefox(options=options) as driver:
        download_audio(args.url, driver, args.title)
