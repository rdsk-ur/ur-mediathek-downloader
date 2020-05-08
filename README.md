# Tools to download stuff from the UR mediathek

## `download_video.py`

Downloads a video file from the UR Medithek.

### Installation

1. Install the [selenium-wire](https://github.com/wkeeling/selenium-wire) package from pip.
2. Install [youtube-dl](http://ytdl-org.github.io/youtube-dl/)
3. You need to have a `credentials.json` file in the current working directory, which should look like this:

    ``` json
    {
        "account": "vip12345",
        "password": "correcthorsebatterystaple"
    }
    ```

Well, replace the entries with your own login information.

### Usage

    python3 download_video.py https://mediathek2.uni-regensburg.de/playthis/<VIDEO_ID>

The video file will be downloaded and saved in the current working directory.

## `download_audio.py`

Downloads all audio files from a given channel and stores them in the current directory.

### Installation

Install the following python packages:

+ beautifulsoup4
+ requests

### Usage

    python3 download_audio.py https://mediathek2.uni-regensburg.de/list/<CHANNEL_ID>
