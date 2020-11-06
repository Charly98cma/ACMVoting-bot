#!/usr/bin/env python

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, CallbackContext

import msgs

import os
import sys
import sqlite3


# Dict of candidates (the first one is the blank vote)
# "key of the candidate" : "Name of the candidate"
candidates = {"blanco" : "-- VOTO EN BLANCO --",
              "ferrero" : "Álvaro Ferrero"}


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
    conn.execute('''CREATE TABLE IF NOT EXISTS votes_table(
    candidate VARCHAR(64) PRIMARY KEY NOT NULL,
    votes INT NOT NULL,
    UNIQUE(candidate));''')
    print("-> Created 'votes' table")

    # Initialization of candidates (silently ignores duplicates)
    for x in candidates:
        conn.execute('''INSERT OR IGNORE INTO votes_table(candidate, votes)
        VALUES (?, ?)''', (x, 0))
        conn.commit()
        print("-> Created candidate 'x' for the elections")
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
        sendMsg(update, msgs.user_registered)
    else:
        sendMsg(update, msgs.user_already_registered)
    conn.close()


def votar_Command(update, context):
    conn = sqlite3.connect('voters.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT votado FROM registered_users WHERE telegramID=:id''',
                 {'id':update.message.from_user.id})
    # If the value is 0, then the user can vote
    res = (cursor.fetchone())[0]
    if (res is None):
        sendMsg(update, "No puedes votar al no estar registrado/a en la lista de votantes.")
    elif (res == 0):
        keyboard = []
        for x,y in candidates.items():
            keyboard.append(InlineKeyboardButton(y, callback_data=x))
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Elige la candidatura a la que quieres dar tu voto:", reply_markup=reply_markup)
        # Update the user info to mark it has voted
        conn.execute('''UPDATE registered_users SET votado=1 WHERE telegramID=?''', (update.message.from_user.id,))
        conn.commit()
    else:
        # If the value is 1, then the user has already voted
        sendMsg(update, "Solo se permite un voto por cada votante.")
    conn.close()

def voto(update, context):
    query = update.callback_query
    query.answer()
    # Include the vote on the DB
    conn = sqlite3.connect('voters.db')
    # Update the votes on the selected candidate
    conn.execute('''UPDATE votes_table SET votes=votes+1 WHERE candidate=?''', (query.data,))
    conn.commit()
    conn.close()
    query.edit_message_text(text="Muchas gracias por participar en las elecciones de ACM-UPM.")


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
        entry_points = [CommandHandler('start', start_Command), CommandHandler('registrarme', register_Command), CommandHandler('votar', votar_Command)],
        states = {},
    fallbacks = [CommandHandler('votar', votar_Command)]# [CommandHandler('registrarme', register_Command)]
    )

    # Handler of the InlineKeyboardButton
    dp.add_handler(CallbackQueryHandler(voto))
    # Added handlers of commands
    dp.add_handler(conv_handler)

    

    # Init DB
    initDB();

    # Starts the bot
    updater.start_polling(clean = True)
    updater.idle()


if __name__ == "__main__":
    main()
