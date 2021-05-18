import requests
import json

import dateutil.parser
from dateutil import tz

import telegram


def controller():
    SYMBOLS = ["ONE"]
    data = get_current_price(SYMBOLS)

    text = data.get("time", "No Coin")
    for currency in data.get("prices", []).keys():
        price = data.get("prices")[currency]
        text += f"\n{currency} : {price}"

    send_message(text)


def get_current_price(SYMBOLS):
    if len(SYMBOLS) == "":
        return {}

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    parameters = {"symbol": ",".join(SYMBOLS), "convert": "USDT"}
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "b1f81bf1-2f5d-42b3-9b5d-ae2f8867c8d3",
    }

    r = requests.get(url, params=parameters, headers=headers)
    response_json = json.loads(r.text)

    # Extracting data
    currencies = response_json.get("data", [])

    data = {"prices": {}}

    for currency in currencies.keys():
        price = currencies[currency].get("quote", {}).get("USDT", {}).get("price")
        data["prices"][currency] = price

    time = response_json.get("status", {}).get("timestamp", {})

    # Converting date time

    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("Asia/Kolkata")

    time = (
        dateutil.parser.parse(time)
        .replace(tzinfo=from_zone)
        .astimezone(to_zone)
        .strftime("Date %d/%m Time %H:%M")
    )

    data["time"] = time
    return data


# Alert sending module
def send_message(text):

    CHAT_ID = 1750474382
    TOKEN = "1833129188:AAHj951iRskGQ8NjnP426GORf7Vi4sIqpDs"

    telegram.Bot(token=TOKEN).sendMessage(chat_id=CHAT_ID, text=text)


if __name__ == "__main__":
    controller()