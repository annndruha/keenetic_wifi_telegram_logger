# Keenetic Wi-Fi/LAN clients Telegram logger

## [README на русском языке](./README-RU.md)

> Work only with Keenetic routers.

Simple python script which sends you a Telegram message when a device connects or disconnects to Wi-Fi/LAN. Also sends message if router becomes unreachable or comes back online.
Script use REST Keenetic-API.

Machine on which this script is running must be **located outside** the network that you plan to monitor.

The script ask router for list of clients every 5 seconds, but routers have a state update delay, so real refresh rate for device connect ~20 seconds, for disconnect ~1-10 minutes.

## How to run (on Linux server via Docker outside router network)

1. Clone repo and go to cloned folder:
    ```shell
    git clone https://github.com/annndruha/keenetic_wifi_telegram_logger
    cd keenetic_wifi_telegram_logger
    ```

2. Copy example .env-file as .env:
    ```shell
    cp .env.example .env
    ```

3. Change values in .env to you credentials as in copied file (Edit via `nano` etc.). Explanation:
    * WIFI_NAME - Human name of network for show in telegram message (Any value)
    * WIFI_HOST - Router domain
    * WIFI_LOGIN - Router web-interface login
    * WIFI_PASSWORD - Router web-interface password
    * TG_BOT_TOKEN - Token for your bot from [BotFather](https://t.me/BotFather)
    * TG_CHAT_ID - Telegram id of the user who will receive notifications (Or group id)

4. Run container and detach:
    ```shell
    docker compose up -d
    ```

## User notes
A Telegram message consists of the following notations:
* Device connection mark as 🟢 symbol
* Device disconnection mark as 🔴 symbol
* Unregistered devices additionally mark with ⚠️ symbol
* If router became unreachable it marks with 🔥 symbol
* If router back online it marks with ✅ symbol

Device name priority to show in message (take first available name):
* user-defined-name (manually set via router web-interface)
* device-build-in-name (device-side specified name)
* mac-address (if no else name available)

No matter what Wi-Fi network used by device:
* All SSIDs for one router will be monitored

If router became unreachable script will send messages with decreasing frequency:
* every 1 minute if down < 3 minutes
* every 10 minutes if down < 1 hour
* every 30 minutes if down >= 1 hour
* As soon as router back online, back message will be sent

If you need monitor more than one router/domain:
* Just clone repo in several folders `git clone https://github.com/annndruha/keenetic_wifi_telegram_logger another_folder`
* Change .env in every folder according to every router creds
* It's pretty to use icons for many routers like `WIFI_NAME=🏠 HOME`

For debug purpose you may explore what information script receive from router:
* Go to your router web-interface at `https://<your_keenetic_domain>/webcli/rest`
* Send POST request with line (UTL:rci/): `/show/ip/hotspot`