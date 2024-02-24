# This script made for Keenetic routers
# If Wi-FI device connected or disconnected - script send telegram message

import time
import hashlib
import copy

import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
WIFI_NAME = config["WIFI_NAME"]
WIFI_HOST = config["WIFI_HOST"]
WIFI_LOGIN = config["WIFI_LOGIN"]
WIFI_PASSWORD = config["WIFI_PASSWORD"]
TG_BOT_TOKEN = config["TG_BOT_TOKEN"]
TG_CHAT_ID = config["TG_CHAT_ID"]

session = requests.session()
ACTIVE_CLIENTS = {}


def keen_auth(username, password):
    r = session.get(f"{WIFI_HOST}/auth")
    if r.status_code == 401:
        md5 = username + ":" + r.headers["X-NDM-Realm"] + ":" + password
        md5 = hashlib.md5(md5.encode('utf-8'))
        sha = r.headers["X-NDM-Challenge"] + md5.hexdigest()
        sha = hashlib.sha256(sha.encode('utf-8'))
        r_new = session.post(f"{WIFI_HOST}/auth", json={"login": username, "password": sha.hexdigest()})
        if r_new.status_code == 200:
            return True
    elif r.status_code == 200:
        return True
    else:
        return False


def update_clients():
    r = session.get(f"{WIFI_HOST}/rci/show/ip/hotspot")
    if r.status_code != 200:
        raise ConnectionRefusedError(f"Status code: {r.status_code}")

    json_clients = r.json()['host']
    for client in json_clients:
        if client['active']:
            ACTIVE_CLIENTS[client['mac']] = client['name'] or client['hostname'] or client['mac']
        else:
            ACTIVE_CLIENTS.pop(client['mac'], None)


def compare_states(old, new):
    new_keys = list(set(new.keys()) - set(old.keys()))
    removed_keys = list(set(old.keys()) - set(new.keys()))
    message = ''
    for nc in new_keys:
        message += f'➕ {new[nc]}%0A'

    for rc in removed_keys:
        message += f'➖ {old[rc]}%0A'

    if len(message):
        message = f'📶 {WIFI_NAME}:%0A' + message
    return message


def send_message(message):
    if not len(message):
        return
    requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
                  f"?chat_id={TG_CHAT_ID}"
                  f"&parse_mode=HTML"
                  f"&text={message}")


if __name__ == "__main__":
    while True:
        try:
            while keen_auth(WIFI_LOGIN, WIFI_PASSWORD):
                old_state = copy.deepcopy(ACTIVE_CLIENTS)
                update_clients()
                message = compare_states(old_state, ACTIVE_CLIENTS)
                send_message(message)
                time.sleep(5)
        except Exception as err:
            print(err)
            time.sleep(30)
