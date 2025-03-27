"""
https://github.com/annndruha/keenetic_wifi_telegram_logger

This script made for Keenetic routers
If Wi-FI device connected or disconnected - script send telegram message
Also send alert if router unreachable
"""
import copy
import hashlib
import logging
import time

import requests
from dotenv import dotenv_values

# Load .env-file
config = dotenv_values('.env')
WIFI_NAME = config['WIFI_NAME']
WIFI_HOST = config['WIFI_HOST']
WIFI_LOGIN = config['WIFI_LOGIN']
WIFI_PASSWORD = config['WIFI_PASSWORD']
TG_BOT_TOKEN = config['TG_BOT_TOKEN']
TG_CHAT_ID = config['TG_CHAT_ID']

# Setup logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S UTC')
logging.Formatter.converter = time.gmtime

# Global session for prevent auth every request
session = requests.session()

# Current connected clients
# {'mac_address' : 'device_name'}
ACTIVE_CLIENTS: dict[str, str] = {}


def keen_auth():
    """Return True if authorized, raise Error if connection is lost"""
    r = session.get(f'{WIFI_HOST}/auth', timeout=10)
    if r.status_code == 200:
        return True
    if r.status_code == 401:
        md5 = WIFI_LOGIN + ':' + r.headers['X-NDM-Realm'] + ':' + WIFI_PASSWORD
        md5 = hashlib.md5(md5.encode('utf-8'))
        sha = r.headers['X-NDM-Challenge'] + md5.hexdigest()
        sha = hashlib.sha256(sha.encode('utf-8'))
        r_auth = session.post(f'{WIFI_HOST}/auth', json={'login': WIFI_LOGIN, 'password': sha.hexdigest()}, timeout=10)
        if r_auth.status_code == 200:
            return True
        else:
            raise requests.HTTPError(f'While auth attempt host return {r_auth.status_code} status code.')
    raise requests.HTTPError(f'While check current auth status host return {r.status_code} status code.')


def update_clients():
    """Update ACTIVE_CLIENTS global variable"""
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


def compare_states(old: dict[str, str], new: dict[str, str]) -> str:
    """Compare states of old and new dicts of clients. Generate message if states is different"""
    new_devices = list(set(new.keys()) - set(old.keys()))
    old_devices = list(set(old.keys()) - set(new.keys()))

    if not len(new_devices) and not len(old_devices):
        return ''

    msg = ''
    msg += ''.join([f'🟢 {new[nc]}%0A' for nc in new_devices])
    msg += ''.join([f'🔴 {old[rc]}%0A' for rc in old_devices])
    msg = '%0A'.join(sorted(filter(None, msg.split('%0A'))))  # Sort devices
    msg = f'{WIFI_NAME}:%0A' + msg
    return msg


def send_message(msg: str):
    if not len(msg):
        return

    logging.info(f'[Send message] {msg}')
    r = requests.post(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?parse_mode=HTML'
                      f'&chat_id={TG_CHAT_ID}&text={msg}', timeout=10)
    if r.status_code != 200:
        logging.error(f'[Telegram error] {r.status_code}, {r.text}')


def get_interval(last_alive: float) -> float:
    """Define interval for host down message (decrease frequency)"""
    elapsed_time = time.time() - last_alive
    if elapsed_time < 180:  # If down < 3 minutes
        return 60  # send every 1 minute
    elif elapsed_time < 3600:  # If down < 1 hour
        return 600  # send every 10 minutes
    else:  # If down >= 1 hour
        return 1800  # send every 30 minutes


def get_human_downtime(last_alive: float) -> str:
    """String representation of downtime"""
    downtime = int(time.time() - last_alive)
    hours, remainder = divmod(downtime, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f'{hours}h {minutes}m {seconds}s'
    elif minutes:
        return f'{minutes}m {seconds}s'
    else:
        return f'{seconds}s'


if __name__ == '__main__':
    host_alive = False
    last_alive = time.time()
    last_sent_time = 0
    while True:
        try:
            try:
                while keen_auth():
                    # Host back online but may have no clients
                    if not host_alive:
                        host_alive = True
                        downtime = get_human_downtime(last_alive)
                        send_message(f'✅ {WIFI_NAME} host alive! (Down for {downtime})')

                    # Send message if state changed
                    old_active_clients = copy.deepcopy(ACTIVE_CLIENTS)
                    update_clients()
                    message = compare_states(old_active_clients, ACTIVE_CLIENTS)
                    send_message(message)

                    # Remember last alive time
                    last_alive = time.time()
                    last_sent_time = 0
                    time.sleep(5)
            except (ConnectionError, requests.RequestException) as e:
                # Router became unreachable or still down
                ACTIVE_CLIENTS = {}
                host_alive = False

                # Send and with decrease frequency
                if time.time() - last_sent_time >= get_interval(last_alive):
                    logging.error(e)
                    downtime = get_human_downtime(last_alive)
                    send_message(f'🔥 {WIFI_NAME} host down ({downtime})')
                    last_sent_time = time.time()
                time.sleep(5)
        except Exception as e:
            logging.exception(e)
            time.sleep(60)
