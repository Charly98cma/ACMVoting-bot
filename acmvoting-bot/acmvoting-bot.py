#!/usr/bin/env python

from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler

import msgs

import os
import sys
import sqlite3


# List of candidates (the first one is the blank vote)
candidates = ["blanco", "ferrero"]


######################
# AUXILIAR FUNCTIONS #
######################

def initDB():
    conn = sqlite3.connect('voters.db')
    print("-> Connected to the DB")
    # Creation of the table 'registered_users'
    conn.execute('''CREATE TABLE IF NOT EXISTS registered_users(
    telegramID VARCHAR(64) PRIMARY KEY NOT NULL,
    alias VARCHAR(64) NOT NULL,
    fullName VARCHAR(64) NOT NULL);''')
    print("-> Created 'registered_users' table")

    # Creation of the table 'votes' with unique candidates
    conn.execute('''CREATE TABLE IF NOT EXISTS votes(
    candidate VARCHAR(64) PRIMARY KEY NOT NULL,
    votes INT NOT NULL,
    UNIQUE(candidate));''')
    print("-> Created 'votes' table")

    # Initialization of candidates (silently ignores duplicates)
    for x in candidates:
        conn.execute('''INSERT OR IGNORE INTO votes(candidate, votes)
        VALUES (?, ?)''', (x, 0))
        conn.commit()
    print("-> Created candidates for the elections")
    # Applies the INSERTS
    conn.close()
    
def sendMsg(update, msg):
    update.message.reply_text(
        text = msg,
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
    # Check if user is already on the DB
    cursor.execute('''SELECT * FROM registered_users WHERE telegramID=:id''',
                   {'id':update.message.from_user.id})
    if (cursor.fetchone() is None):
        # User is added to the DB with its username as key and the full name as value
        cursor.execute('''INSERT INTO registered_users values (:telegramid, :alias, :fullname)''',
                       {'telegramid':update.message.from_user.id, 'alias':update.message.from_user.username, 'fullname': update.message.from_user.full_name})
        conn.commit()
        conn.close()
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

    # Init DB
    initDB();

    # Starts the bot
    updater.start_polling(clean = True)
    updater.idle()


if __name__ == "__main__":
    main()
