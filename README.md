# Keenetic Wi-Fi/LAN clients Telegram logger

> Work only with Keenetic routers.

Simple python script which sends you a Telegram message when a device connects to Wi-Fi/LAN or disconnects. Also sends message if router becomes unreachable or comes back online.
Script use REST Keenetic-API. For test propose check your router web-interface at `https://<YOURDOMAIN>.keenetic.<pro|link|name>/a`

Machine on which this script is running must be **located outside** the network that you plan to monitor.

The script ask router for list of clients every 5 seconds, but routers have a state update delay, so real refresh rate for device connect ~20 seconds for disconnect ~1-10 minutes.

## How to run (on Linux server outside Wi-Fi network + docker)

1. Clone repo and go to cloned folder:
    ```shell
    git clone https://github.com/annndruha/keenetic_wifi_telegram_logger
    cd keenetic_wifi_telegram_logger
    ```

2. Copy example .env-file:
    ```shell
    cp .env.example .env
    ```

3. Change values in .env-file to you credentials as in copied example (Edit via `nano` etc.). Explanation:
    * WIFI_NAME - Human name of network for show in telegram message (Any value)
    * WIFI_HOST - Router domain
    * WIFI_LOGIN - Router admin-panel login
    * WIFI_PASSWORD - Router admin-panel password
    * TG_BOT_TOKEN - Token for your bot from BotFather
    * TG_CHAT_ID - Telegram id of the user who will receive notifications (Or group id)

4. Run container and detach:
    ```shell
    docker compose up -d
    ```

## User notes
A Telegram message consists of the following notations:
* Device connection mark as 🟢 symbol
* Device disconnection mark as 🔴 symbol
* Unregistered devices also mark with ⚠️ symbol
* If router became unreachable it marks with 🔥 symbol

Device name order to show in message (take first available name):
* user-defined-name (manually set via router web-interface)
* device-build-in-name (device-side specified name)
* mac-address (if no else name available)

No matter what SSID used by device.
* All SSIDs for one router will be monitored

Unreachable message rules:
* If router became unreachable script will send messages with decreasing frequency
* every 1 minute if down < 3 minutes
* every 10 minutes if down < 1 hour
* every 30 minutes if down >= 1 hour
* As soon as router back online, back message will be sent