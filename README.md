# Tools to download stuff from the UR mediathek

This repository contains scripts to download assets from the UR mediathek.

If you have suggestions or found bugs, feel free to open an issue or create a pull request!

## Installation

1. Install Python
2. Install the `requests` package using `pip install requests`.
3. Install the [VLC media player](https://www.videolan.org/vlc/). We use VLC to do the stream conversion.

You need to create a `credentials.json` file in this directory with the following content:

``` json
{
    "username": "vip12345",
    "password": "correcthorsebatterystaple"
}
```

Well, replace the entries with your own login information.

Tip: Restrict the read permissions to the `credentials.json` file, e.g. on linux: `chmod 600 credentials.json`

## `video.py`

Downloads a video file from the UR Medithek.

Using you browser, navigate to the video in the mediathek. Copy the full URL (should begin with `https://mediathek2.uni-regensburg.de/playthis/`). Then, run

    python3 video.py <COPIED_URL>

The video file will be downloaded and saved in the current working directory.

Use `python3 video.py --help` to show more options.

## `audio.py`

Downloads an audio file from the mediathek and stores it in the current directory.

Using you browser, navigate to the video in the mediathek. Copy the full URL (should begin with `https://mediathek2.uni-regensburg.de/playthis/`). Then, run

    python3 audio.py <COPIED_URL>

Use `python3 audio.py --help` to show more options.
