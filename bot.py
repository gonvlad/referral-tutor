import os
import telebot
from telebot import types
import logging
from flask import Flask, request
from text_templates import START_TEXT
from text_templates import HR_MANAGER_NOTIFICATION_TEXT
from text_templates import TECH_MANAGER_NOTIFICATION_TEXT
from text_templates import ACCEPT_TASK_BUTTON_TEXT
from text_templates import ACCEPT_TASK_BUTTON_DATA
from text_templates import LINK_BUTTON_TEXT
from text_templates import LINK_BUTTON_DATA
from text_templates import SUBMIT_TASK_BUTTON_TEXT
from text_templates import SUBMIT_TASK_BUTTON_DATA
from text_templates import CREDENTIALS
from text_templates import VERIFICATION_IN_PROGRESS_TEXT
from credentials_getter import CredentialsGetter


BOT_TOKEN = os.environ['BOT_TOKEN']
APP_URL = os.environ['APP_URL']
HR_MANAGER_ID = os.environ['HR_MANAGER_ID']
TECH_MANAGER_ID = os.environ['TECH_MANAGER_ID']
HR_MANAGER_USERNAME = os.environ['HR_MANAGER_USERNAME']

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)
credentials_getter = CredentialsGetter()

task = {
    "Title" : "OKCOIN", 
    "Text" : "Краткое описание задания:\n\- Заполнить базовую анкету\n\- Верифицировать аккаунт\n\nПодробнее смотрите в инструкции ⬇️", 
    "Instruction_link" : "https://telegra.ph/Instrukciya-verifikaciya-Okcoin-01-08", 
}


@bot.message_handler(commands=['start'])
def start(message):
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
        
        credentials = credentials_getter.get_credentials()
        
        if credentials:
            login = credentials[1]
            password = credentials[2]
        
            markup = types.InlineKeyboardMarkup()
            submit_task_btn = types.InlineKeyboardButton(SUBMIT_TASK_BUTTON_TEXT, callback_data=SUBMIT_TASK_BUTTON_DATA)

            markup.row(submit_task_btn)
            
            id = credentials[0]
            result = credentials_getter.update_credentials(id=id)      
            if result:
                bot.send_message(call.message.chat.id, CREDENTIALS.format(login=login, password=password), reply_markup=markup)
        else:
            number_of_credentials = 0
            bot.send_message(TECH_MANAGER_ID, TECH_MANAGER_NOTIFICATION_TEXT.format(username=username, number_of_credentials=number_of_credentials))
    if str(call.data) == SUBMIT_TASK_BUTTON_DATA:
        manager_username = HR_MANAGER_USERNAME
        username = call.message.chat.username
        
        bot.send_message(call.message.chat.id, VERIFICATION_IN_PROGRESS_TEXT.format(manager_username=manager_username))
        bot.send_message(HR_MANAGER_ID, HR_MANAGER_NOTIFICATION_TEXT.format(username=username))
        bot.send_message(TECH_MANAGER_ID, HR_MANAGER_NOTIFICATION_TEXT.format(username=username))
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