# Keenetic Wi-Fi Telegram Logger

Simple python script which sends a Telegram message when a device is connected to Wi-Fi or disconnected from Wi-Fi

## How to use (linux)

Clone repo:
```shell
git clone https://github.com/annndruha/keenetic_wifi_telegram_logger
```

Create in repo folder .env-file:
```shell
touch .env
```

Fill your values in .env-file (`nano .env` etc.):
```text
WIFI_NAME=human_name_for_message
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