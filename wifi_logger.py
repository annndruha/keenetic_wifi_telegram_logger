# https://github.com/annndruha/keenetic_wifi_telegram_logger
# This script made for Keenetic routers
# If Wi-FI device connected or disconnected - script send telegram message
# Also send in router down

import time
import hashlib
import copy
import logging

import requests
from dotenv import dotenv_values

config = dotenv_values('.env')
WIFI_NAME = config['WIFI_NAME']
WIFI_HOST = config['WIFI_HOST']
WIFI_LOGIN = config['WIFI_LOGIN']
WIFI_PASSWORD = config['WIFI_PASSWORD']
TG_BOT_TOKEN = config['TG_BOT_TOKEN']
TG_CHAT_ID = config['TG_CHAT_ID']

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%Y.%m.%d %H:%M:%S UTC'
)
logging.Formatter.converter = time.gmtime

session = requests.session()  # Global session for prevent auth on every request
ACTIVE_CLIENTS = {}  # {'mac_address' : 'device_name'}


def keen_auth(username, password):
    r = session.get(f'{WIFI_HOST}/auth', timeout=10)
    if r.status_code == 200:
        return True
    if r.status_code == 401:
        md5 = username + ':' + r.headers['X-NDM-Realm'] + ':' + password
        md5 = hashlib.md5(md5.encode('utf-8'))
        sha = r.headers['X-NDM-Challenge'] + md5.hexdigest()
        sha = hashlib.sha256(sha.encode('utf-8'))
        r_auth = session.post(f'{WIFI_HOST}/auth', json={'login': username, 'password': sha.hexdigest()}, timeout=10)
        if r_auth.status_code == 200:
            return True
        else:
            raise requests.HTTPError(f'While auth attempt host return {r_auth.status_code} status code.')
    raise requests.HTTPError(f'While check current auth status host return {r.status_code} status code.')


def update_clients():
    r = session.get(f'{WIFI_HOST}/rci/show/ip/hotspot', timeout=10)
    if r.status_code != 200:
        raise ConnectionRefusedError(f'Status code: {r.status_code}')

    json_clients = r.json()['host']
    for client in json_clients:
        if client['active']:
            client_name = client['name'] or client['hostname'] or client['mac']
            if not client['registered']:
                client_name = '⚠️ ' + client_name
            ACTIVE_CLIENTS[client['mac']] = client_name
        else:
            ACTIVE_CLIENTS.pop(client['mac'], None)  # Delete from clients list


def compare_states(old, new):
    new_devices = list(set(new.keys()) - set(old.keys()))
    old_devices = list(set(old.keys()) - set(new.keys()))

    if not len(new_devices) and not len(old_devices):
        return ''

    msg = ''
    msg += ''.join([f'🟢 {new[nc]}%0A' for nc in new_devices])
    msg += ''.join([f'🔴 {old[rc]}%0A' for rc in old_devices])
    msg = '%0A'.join(sorted(filter(None, msg.split('%0A'))))
    msg = f'{WIFI_NAME}:%0A' + msg
    return msg


def send_message(msg):
    if not len(msg):
        return

    logging.info(f'[Send message] {msg}')
    r = requests.post(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?parse_mode=HTML'
                      f'&chat_id={TG_CHAT_ID}&text={msg}', timeout=10)
    if r.status_code != 200:
        logging.error(f'[Telegram error] {r.status_code}, {r.text}')


if __name__ == '__main__':
    host_alive = True
    while True:
        try:
            try:
                while keen_auth(WIFI_LOGIN, WIFI_PASSWORD):
                    if not host_alive:  # Host back online but may have no clients
                        host_alive = True
                        send_message(f'✅ {WIFI_NAME} host alive!')
                    old_active_clients = copy.deepcopy(ACTIVE_CLIENTS)
                    update_clients()
                    message = compare_states(old_active_clients, ACTIVE_CLIENTS)
                    send_message(message)
                    time.sleep(5)
            except (ConnectionError, requests.RequestException) as err:
                ACTIVE_CLIENTS = {}
                host_alive = False
                logging.error(err)
                send_message(f'🔥 {WIFI_NAME} host probably down.')
                time.sleep(30)
        except Exception as err:
            logging.error(err)
            time.sleep(30)
