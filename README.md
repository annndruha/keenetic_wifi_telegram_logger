# Keenetic Wi-Fi/LAN clients Telegram logger

> Work only with Keenetic routers.

Simple python script which sends you a Telegram message when a device connects to Wi-Fi/LAN or disconnects. Also sends message if router becomes unreachable or comes back online.
Script use REST Keenetic-API. For test propose check your router web-interface at `https://<YOURDOMAIN>.keenetic.<pro|link|name>/a`

Machine on which this script is running must be located outside the network that you plan to monitor.

The script ask router for list of clients every 5 seconds, but routers have a state update delay, so real refresh rate for device connect ~20 seconds for disconnect ~1-10 minutes.

## How to use (Linux + docker)

Clone repo and go to folder:
```shell
git clone https://github.com/annndruha/keenetic_wifi_telegram_logger
cd keenetic_wifi_telegram_logger
```

Create in .env-file in repository folder:
```shell
touch .env
```

Fill your values in .env-file (`nano .env` etc.) as in example:

(TG_CHAT_ID - Telegram id of the user who will receive notifications)

```text
WIFI_NAME=🏠 Home Wi-Fi
WIFI_HOST=https://yourdomain.keenetic.pro
WIFI_LOGIN=admin
WIFI_PASSWORD=password
TG_BOT_TOKEN=123456:ABCDEFGHIJKLMNFSSJFKAGS
TG_CHAT_ID=123456789
```

Run container:
```shell
docker compose up -d
```

## User notes
A Telegram message consists of the following notations:
* Device connection mark as 🟢 symbol
* Device disconnection mark as 🔴 symbol
* Unregistered devices also mark with symbol ⚠️
* If router became unreachable marks with 🔥 symbol and send error description

Device name order to show in message (take first available name):
* user-defined-name (manually set via router web-interface)
* device-build-in-name (device-side specified name)
* mac-address (if no else name available)
