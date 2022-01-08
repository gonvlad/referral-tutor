import os
import telebot
from telebot import types
import logging
from flask import Flask, request
from text_templates import START_TEXT
from text_templates import ACCEPT_TASK_BUTTON_TEXT
from text_templates import ACCEPT_TASK_BUTTON_DATA
from text_templates import LINK_BUTTON_TEXT
from text_templates import LINK_BUTTON_DATA
from text_templates import CREDENTIALS


BOT_TOKEN = os.environ['BOT_TOKEN']
APP_URL = os.environ['APP_URL']


bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
def start(message):
    task = {"Title" : "OKCOIN", "Text" : "Краткое описание задания:\n\- Заполнить базовую анкету\n\- Верифицировать аккаунт\n\nПодробнее смотрите в инструкции ⬇️", "Instruction_link" : "https://telegra.ph/Instrukciya-verifikaciya-Okcoin-01-08" }
    text = task["Text"]
    instruction_link = task["Instruction_link"]
    
    markup = types.InlineKeyboardMarkup()
    link_btn = types.InlineKeyboardButton(LINK_BUTTON_TEXT, url=instruction_link, callback_data=LINK_BUTTON_DATA)
    accept_task_btn = types.InlineKeyboardButton(ACCEPT_TASK_BUTTON_TEXT, callback_data=ACCEPT_TASK_BUTTON_DATA)

    markup.row(link_btn)
    markup.row(accept_task_btn)
    
    bot.send_message(message.chat.id, START_TEXT)
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='MarkdownV2')
    

@bot.callback_query_handler(func=lambda call: True)
def handle_accept(call):
    if str(call.data) == ACCEPT_TASK_BUTTON_DATA:
        login = "petrovich@gmail.com"
        password = "12345678"
        bot.send_message(call.message.chat.id, CREDENTIALS.format(login=login, password=password))
    bot.answer_callback_query(call.id)


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))