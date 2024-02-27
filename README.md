# Keenetic Wi-Fi Telegram Logger

Simple python script which sends you a Telegram message when a device connected to Wi-Fi or disconnected.
Work only with Keenetic routers. Script use REST (over CLI) Keenetic-API. For test propose check your router web-interface at `https://yourdomain.keenetic.pro/a`

Script ask router for list of clients every 5 seconds, but routers has delay for updated state, so real refresh rate for connect ~20 seconds for disconnect ~1-20 minutes.

## How to use (Linux)

Clone repo and go to folder:
```shell
git clone https://github.com/annndruha/keenetic_wifi_telegram_logger
cd keenetic_wifi_telegram_logger
```

Create in .env-file repository folder :
```shell
touch .env
```

Fill your values in .env-file (`nano .env` etc.):
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