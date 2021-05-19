import requests
import json

import dateutil.parser
from dateutil import tz
import os

from telegram.ext import Updater, CommandHandler, CallbackContext
from decimal import *

INTERVAL = 900


def controller(context: CallbackContext):
    with open("symbol_data_.json") as f:
        SYMBOLS = json.load(f)

    data = get_current_price(SYMBOLS)

    text = data.get("time", "No Coin")
    for currency in data.get("prices", {}).keys():
        price = data.get("prices")[currency]
        text += f"\n{currency} : {price}"

    send_message(context, text)


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
def send_message(context, text):
    context.bot.sendMessage(chat_id=context.job.context, text=text)


def start(update, context):
    context.job_queue.run_repeating(
        controller, interval=INTERVAL, first=0, context=update.message.chat_id
    )


def set_interval(update, context):
    text = update.message.text
    INTERVAL = int(text.replace("/si", "").strip())

    context.job_queue.stop()
    context.job_queue.run_repeating(
        controller, interval=INTERVAL, first=0, context=update.message.chat_id
    )


def stop(update, context):
    context.job_queue.stop()


def get_price(update, context):
    text = update.message.text
    SYMBOL = text.replace("/gp", "").strip()

    data = get_current_price([SYMBOL])

    text = data.get("time", "No Coin")
    for currency in data.get("prices", []).keys():
        price = data.get("prices")[currency]
        text += f"\n{currency} : {price}"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def add_symbol_to_scheduler(update, context):
    text = update.message.text
    symbol = text.replace("/ats", "").strip()

    with open("symbol_data_.json") as f:
        SYMBOLS = json.load(f)

    SYMBOLS.append(symbol)

    with open("symbol_data_.json", "w") as f:
        json.dump(SYMBOLS, f)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Success")


def show_scheduler_symbols(update, context):
    with open("symbol_data_.json") as f:
        SYMBOLS = json.load(f)

    text = ""
    if len(SYMBOLS) == 0:
        text = "No Symbols Yet"
    for sym in SYMBOLS:
        text += f"{sym}\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remove_symbol_from_scheduler(update, context):
    text = update.message.text
    SYMBOL = text.replace("/rfs", "").strip()

    with open("symbol_data_.json") as f:
        SYMBOLS = json.load(f)

    if len(SYMBOLS) == 0:
        text = "No Symbols Yet"
    else:
        SYMBOLS.remove(SYMBOL)

        with open("symbol_data_.json", "w") as f:
            json.dump(SYMBOLS, f)
        text = "Success"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def add_to_portfolio(update, context):
    symbol = ""
    total_amount_paid = Decimal(0)
    bought_price = Decimal(0)

    symbol = symbol.upper()
    order = {
        "total_amount_paid": total_amount_paid,
        "total_amount_bought": total_amount_paid / bought_price,
    }

    {"BTC": {"total_amount_paid": 10, "total_amount_bought": 10}}
    # average_price = total_amount_paid/total_amount_bought

    with open("portfolio.json") as f:
        portfolio_data = json.load(f)

    if symbol in portfolio_data.keys():
        asset = portfolio_data[symbol]
        updated_asset = {}

        for key in asset.keys():
            updated_asset[key] = str(Decimal(asset[key]) + order[key])

        portfolio_data[symbol] = updated_asset
    else:
        for key in order.keys():
            order[key] = str(order[key])
        portfolio_data[symbol] = order

    with open("portfolio.json", "w") as f:
        json.dump(portfolio_data, f)


def main():
    PORT = int(os.environ.get("PORT", "8443"))
    APP_NAME = "botmanager897"

    TOKEN = "1833129188:AAHj951iRskGQ8NjnP426GORf7Vi4sIqpDs"
    updater = Updater(token=TOKEN, use_context=True)

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{APP_NAME}.herokuapp.com/{TOKEN}",
    )

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("si", set_interval))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("gp", get_price))
    dispatcher.add_handler(CommandHandler("ats", add_symbol_to_scheduler))
    dispatcher.add_handler(CommandHandler("ss", show_scheduler_symbols))
    dispatcher.add_handler(CommandHandler("rfs", remove_symbol_from_scheduler))

    updater.idle()


if __name__ == "__main__":
    main()