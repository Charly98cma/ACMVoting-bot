#!/usr/bin/env python

from telegram import Update
from telegra.ext import Updater, CommandHandler

from msgs import *

import os
import sys
import sqlite3


def start_Command(update, context):
    update.message.reply_text(
        test = start_msg,
        parse_mode="html"
    )

def register_Command(update, context):
    global conn
    global cursor

    # Telegram username (@...)
    username = update.message.from_user.username
    # Check if user is already on the DB
    cursor.execute('''SELECT * FROM registered_users WHERE telegramID=:username''',
                   {'username':username})
    if (cursor.fetchone() is None):
        # User is added to the DB with its username as key and the full name as value
        cursor.execute('''INSERT INTO registered_users values (:username, :fullname)''',
                       {'username':username, 'fullname': update.message.from_user.full_name})
        conn.commit()

        update.message.reply_text(
            text = user_registered,
            parse_mode="html"
        )
    else:
        update.message.reply_text(
            text = user_already_registered,
            parse_mode="html"
        )


def main():
    # TOKEN
    if 'VOTING_TOKEN' not in os.environ:
        print("Environment variable 'VOTING_TOKEN' not defined.", file=sys.stderr)
        exit(1)

    updater = Updater(
        token = os.environ.get('VOTING_TOKEN'),
        use_context = True
    )

    # Dispatcher
    dp = updater.dispatcher

    # Handlers
    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start_Command)],
        states = {}, # States aren't required yet
        fallbacks = [CommandHandler('registrarme', register_Command)]
    )
    dp.add_handler(conv_handler)

    # Connection with the DB (must be a global variable)
    conn = sqlite3.connect('voters.db')
    print("-> Connected to the DB")

    conn.execute('''CREATE TABLE IF NOT EXISTS registered_users(
    telegramID VARCHAR(64) PRIMARY KEY,
    fullName VARCHAR(64) NOT NULL);''')

    cursor = conn.cursor()
    
    # Starts the bot
    updater.start_polling(clean = True)
    updater.idle()


if __name__ == "__main__":
    main()
