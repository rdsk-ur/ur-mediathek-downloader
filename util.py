import json
import os


def get_credentials():
    credentials_path = os.path.dirname(os.path.realpath(__file__)) + "/credentials.json"
    try:
        with open(credentials_path) as credentials_file:
            return json.load(credentials_file)
    except FileNotFoundError:
        print(credentials_path, "is missing. Please read the readme for more details")
    except json.decoder.JSONDecodeError:
        print("credentials.json is no valid JSON file")


def authenticate(driver, credentials):
    print("Enter credentials")
    acount_name = credentials["account"]
    password = credentials["password"]
    driver.execute_script(f"document.querySelector('#frmLoginRzaccout').value='{acount_name}'")
    driver.execute_script(f"document.querySelector('#frmLoginPassword').value='{password}'")
    driver.execute_script('document.querySelector("form.form-signin button").click()')
