#!/usr/bin/env python3
import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

from util import authenticate, get_credentials
from audio import download_audio
from video import download_video

def main(channel_url):
    try:
        credentials = get_credentials()
    except:
        return

    print("Launch headless firefox")
    options = Options()
    options.headless = True
    with webdriver.Firefox(options=options) as driver:
        driver.get("https://mediathek2.uni-regensburg.de/login")
        authenticate(driver, credentials)
        time.sleep(5)

        driver.get(channel_url)

        asset_urls = []
        for entry in driver.find_elements_by_css_selector("div.urtube-asset-card"):
            asset_url = entry.find_element_by_css_selector("a").get_attribute("href")
            if entry.find_element_by_css_selector("img").get_attribute("src") == "https://mediathek2.uni-regensburg.de/img/audio-only.png":
                # audio
                print("audio @", asset_url)
                asset_urls.append((asset_url, False))
            else:
                # video
                print("video @", asset_url)
                asset_urls.append((asset_url, False))

        for asset_url, is_video in asset_urls:
            if is_video:
                download_video(asset_url, driver)
            else:
                download_audio(asset_url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "CHANNEL_URL")
        exit(1)
    main(sys.argv[1])
