# https://github.com/annndruha/keenetic_wifi_telegram_logger
# This script made for Keenetic routers
# If Wi-FI device connected or disconnected - script send telegram message
# Also send in router down

import json
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
ACTIVE_CLIENTS = {}  # {mac : name}


def keen_auth(username, password):
    r = session.get(f'{WIFI_HOST}/auth')
    if r.status_code == 401:
        md5 = username + ':' + r.headers['X-NDM-Realm'] + ':' + password
        md5 = hashlib.md5(md5.encode('utf-8'))
        sha = r.headers['X-NDM-Challenge'] + md5.hexdigest()
        sha = hashlib.sha256(sha.encode('utf-8'))
        r_new = session.post(f'{WIFI_HOST}/auth', json={'login': username, 'password': sha.hexdigest()})
        if r_new.status_code == 200:
            return True
    elif r.status_code == 200:
        return True
    else:
        return False


def update_clients():
    # r = session.get(f'https://gdssgddgs.com/rci/show/ip/hotspot')
    r = session.get(f'{WIFI_HOST}/rci/show/ip/hotspot')
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
    new_keys = list(set(new.keys()) - set(old.keys()))
    removed_keys = list(set(old.keys()) - set(new.keys()))
    msg = ''
    msg += ''.join([f'🟢 {new[nc]}%0A' for nc in new_keys])
    msg += ''.join([f'🔴 {old[rc]}%0A' for rc in removed_keys])
    msg = '%0A'.join(sorted(filter(None, msg.split('%0A'))))

    if len(msg):  # If changed, also specify Wi-Fi alias
        msg = f'{WIFI_NAME}:%0A' + msg
    return msg


def send_message(message):
    if not len(message):
        return

    logging.info('[Send message]' + message)
    r = requests.post(f'https://api.telegram.org'
                      f'/bot{TG_BOT_TOKEN}'
                      f'/sendMessage'
                      f'?chat_id={TG_CHAT_ID}'
                      f'&parse_mode=HTML'
                      f'&text={message}')
    if r.status_code != 200:
        logging.error(f'[Telegram error] {r.status_code}, {r.text}')


def send_host_down_message(error):
    """
    At first glance, it seems that this function can be removed,
    but otherwise unable to send a message with a quote
    """
    def utf16len(text):
        i = 0
        for c in text:
            i += 1 if ord(c) < 65536 else 2
        return i
    unquoted_text = f'🔥 {WIFI_NAME} host probably down.'
    offset = utf16len(unquoted_text)
    length = utf16len(str(error))

    host_down_message = unquoted_text + str(error)

    body = {'chat_id': TG_CHAT_ID,
            'text': host_down_message,
            'entities': json.dumps([{'type': 'blockquote',
                                     'offset': offset,
                                     'length': length}])}
    r = requests.post(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage', data=body)
    if r.status_code != 200:
        logging.error(f'[Telegram error] {r.status_code}, {r.text}')


if __name__ == '__main__':
    while True:
        try:
            try:
                while keen_auth(WIFI_LOGIN, WIFI_PASSWORD):
                    old_state = copy.deepcopy(ACTIVE_CLIENTS)
                    update_clients()
                    send_message(compare_states(old_state, ACTIVE_CLIENTS))
                    time.sleep(5)
            except (ConnectionError, requests.RequestException) as err:
                logging.error(err)
                send_host_down_message(err)
                time.sleep(30)
        except Exception as err:
            logging.error(err)
            time.sleep(10)
