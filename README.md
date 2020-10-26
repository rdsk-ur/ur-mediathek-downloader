# Tools to download stuff from the UR mediathek

This repository contains scripts to download assets from the UR mediathek.

If you have suggestions or found bugs, feel free to post an issue or create a pull request!

## Installation

If you use [Poetry](https://python-poetry.org/), you can run `poetry install` to setup a python environment with the required packages.

Alternatively, you can use the `requirements.txt` file and run `pip install -r requirements.txt`.

You can also manually install the following packages:

+ requests
+ selenium-wire

After you have installed the python packages, you have to install [youtube-dl](https://youtube-dl.org/).

## `video.py`

Downloads a video file from the UR Medithek.

Using you browser, navigate to the video in the mediathek. Copy the full URL (should look like `https://mediathek2.uni-regensburg.de/playthis/<VIDEO_ID>`). Then, run

    python3 video.py <COPIED_URL>

The video file will be downloaded and saved in the current working directory.

Use `python3 video.py --help` to show more options.

### Requirements

This script launches a headless Firefox browser instance to query the website. If you wish to use another browser you have to edit the `video.py` and replace `firefox` with the respective choice.

You need to have a `credentials.json` file in the same directory as `video.py` with the following content:

``` json
{
    "account": "vip12345",
    "password": "correcthorsebatterystaple"
}
```

Well, replace the entries with your own login information.

Tip: Restrict the read permissions to the `credentials.json` file, e.g. on linux: `chmod 600 credentials.json`


## `audio.py`

Downloads an audio file from the mediathek and stores it in the current directory.

Using you browser, navigate to the video in the mediathek. Copy the full URL (should look like `https://mediathek2.uni-regensburg.de/playthis/<AUDIO_ID>`). Then, run

    python3 audio.py <COPIED_URL>

## `channel.py`

Utility script to download all assets from a given channel.

    python3 channel.py <CHANNEL_URL>
