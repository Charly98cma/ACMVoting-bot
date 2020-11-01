#!/usr/bin/env python

from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler

import msgs

import os
import sys
import sqlite3

######################
# AUXILIAR FUNCTIONS #
######################

def sendMsg(update, msg):
    update.message.reply_text(
        text = msgs.start_msg,
        parse_mode = "html"
    )

    
##########################
# CONVERSATION FUNCTIONS #
##########################
    
def start_Command(update, context):
    sendMsg(update, msgs.start_msg)

def register_Command(update, context):
    conn = sqlite3.connect('voters.db')
    cursor = conn.cursor()
    # Telegram username (@...)
    telegramid = update.message.from_user.id
    # Check if user is already on the DB
    cursor.execute('''SELECT * FROM registered_users WHERE telegramID=:id''',
                   {'id':telegramid})
    if (cursor.fetchone() is None):
        # User is added to the DB with its username as key and the full name as value
        cursor.execute('''INSERT INTO registered_users values (:telegramid, :alias, :fullname)''',
                       {'telegramid':telegramid, 'alias':update.message.from_user.username, 'fullname': update.message.from_user.full_name})
        conn.commit()
        sendMsg(update, msgs.user_registered)
    else:
        sendMsg(update, msgs.user_already_registered)


########
# MAIN #
########
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
        entry_points = [CommandHandler('start', start_Command), CommandHandler('registrarme', register_Command)],
        states = {}, # States aren't required yet
        fallbacks = [CommandHandler('registrarme', register_Command)]
    )
    dp.add_handler(conv_handler)

    # Connection with the DB (must be a global variable)
    conn = sqlite3.connect('voters.db') 
    print("-> Connected to the DB")
    # Creation of the table if doesn't exists
    conn.execute('''CREATE TABLE IF NOT EXISTS registered_users(
    telegramID VARCHAR(64) PRIMARY KEY,
    alias VARCHAR(64) NOT NULL,
    fullName VARCHAR(64) NOT NULL);''')
    cursor = conn.cursor()
    
    # Starts the bot
    updater.start_polling(clean = True)
    updater.idle()


if __name__ == "__main__":
    main()
