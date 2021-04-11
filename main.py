from flask import Flask
from data import db_session
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler

'''
USERNAME = 'root'
PASSWORD = 'root'
HOST = 'localhost'
DBNAME = 'firstcarhelp'
'''
TOKEN = 'guess it'


def echo(update, context):
    update.message.reply_text(update.message.text)


def main():
    db_session.global_init('db/main.db')
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()