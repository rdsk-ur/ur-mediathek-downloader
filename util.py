import json
import os
import re
from logging import info, error

from requests import Session


def get_credentials():
    credentials_path = os.path.dirname(os.path.realpath(__file__)) + "/credentials.json"
    try:
        with open(credentials_path) as credentials_file:
            return json.load(credentials_file)
    except FileNotFoundError:
        error(credentials_path, "is missing. Please read the readme for more details")
    except json.decoder.JSONDecodeError:
        error("credentials.json is no valid JSON file")


def get_authenticated_session(credentials):
    info("Authenticating")
    session = Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"

    res = session.get("https://mediathek2.uni-regensburg.de/login")
    token = re.findall(r"name=\"_token\" value=\"(.+)\"", res.text)[0]

    data = {
        "frmLoginRzaccount": credentials["username"],
        "frmLoginPassword": credentials["password"],
        "_token": token
    }
    res = session.post("https://mediathek2.uni-regensburg.de/login", data=data)
    res.raise_for_status()

    return session
