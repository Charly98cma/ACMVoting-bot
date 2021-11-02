#!/usr/bin/env python

from telegram import \
    InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import \
    Updater, CommandHandler, ConversationHandler, CallbackQueryHandler

from datetime import datetime
from os import environ as osEnv
from sys import stderr as STDERR
from sqlite3 import connect as sqlConn
from apscheduler.schedulers.background import BackgroundScheduler

import msgs
import queries


# Dict of candidates (the first one is the blank vote)
# "key of the candidate" : "Name of the candidate"
candidates = {"blanco": "-- VOTO EN BLANCO --",
              "borja": "Borja Martinena"}

# Scheduler to send reminder of voting
sched = BackgroundScheduler()

# VOTING DATE = 15/11/2021
VOTING_DATE = datetime(2021, 11, 15, 8, 0)


######################
# AUXILIAR FUNCTIONS #
######################


def initDB():
    conn = sqlConn('voters.db')
    print("-> Connected to the DB")

    # Creation of the table 'registered_users'
    conn.execute(queries.create_users_table)
    print("-> Created 'registered_users' table")

    # Creation of the table 'votes' with unique candidates
    conn.execute(queries.create_votes_table)
    print("-> Created 'votes' table")

    # Initialization of candidates (silently ignores duplicates)
    for cand in candidates:
        conn.execute(queries.insert_candidate, (cand, 0))
        conn.commit()
        print(f"-> Created candidate '{cand}' for the elections")

    conn.close()


def sendMsg(update, msg):
    update.message.reply_text(
        text=msg,
        parse_mode="html"
    )


##########################
# CONVERSATION FUNCTIONS #
##########################


def start_Command(update, context):
    sendMsg(update, msgs.start_msg)


def register_Command(update, context):

    if datetime.today() >= VOTING_DATE:
        sendMsg(update,
                msgs.register_over_date.format(date=VOTING_DATE.strftime("%d/%m/%Y"),
                                               time=VOTING_DATE.strftime("%H:%M")))
        return

    conn = sqlConn('voters.db')
    cursor = conn.cursor()

    # Check user already registered
    cursor.execute(queries.check_user_registered,
                   {'id': update.message.from_user.id})

    if (cursor.fetchone() is None):
        # Register user with username (key), alias and fullname
        cursor.execute(queries.register_user,
                       {'telegramid': update.message.from_user.id,
                        'alias': update.message.from_user.username,
                        'fullname': update.message.from_user.full_name})
        conn.commit()
        print(f"--> Registered voter '{update.message.from_user.id}' - '{update.message.from_user.alias}'")
        sendMsg(update, msgs.user_registered)

    else:
        sendMsg(update, msgs.user_already_registered)

    conn.close()


def vote_Command(update, context):

    if datetime.today() < VOTING_DATE:
        sendMsg(update,
                msgs.voting_date.format(date=VOTING_DATE.strftime("%d/%m/%Y"),
                                        time=VOTING_DATE.strftime("%H:%M")))
        return

    conn = sqlConn('voters.db')
    cursor = conn.cursor()

    # Check if user already voted
    cursor.execute(queries.check_user_voted,
                   {'id': update.message.from_user.id})

    # If the value is 0, then the user can vote
    res = (cursor.fetchone())[0]

    if (res is None):
        sendMsg(update, msgs.user_not_registered)

    elif (res == 0):
        keyboard = []
        # Add button for each candidate
        for x, y in candidates.items():
            button = [InlineKeyboardButton(y, callback_data=x)]
            keyboard.append(button)

        # Ask for user vote
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(msgs.ask_user_vote,
                                  reply_markup=reply_markup)

        # Update the user info to mark it has voted
        conn.execute(queries.register_user_vote,
                     (update.message.from_user.id,))
        conn.commit()
        print(f"--> User {update.message.from_user.id} voted.")

    else:
        # If the value is 1, then the user has already voted
        sendMsg(update, msgs.user_already_voted)
    conn.close()


def vote(update, context):

    query = update.callback_query
    query.answer()

    # Include the vote on the DB
    conn = sqlConn('voters.db')

    # Update the votes on the selected candidate
    conn.execute(queries.update_vote, (query.data,))
    conn.commit()
    conn.close()

    query.edit_message_text(text=msgs.acm_greetings)


########
# MAIN #
########
def main():

    # TOKEN
    if 'VOTING_TOKEN' not in osEnv:
        print("Environment variable 'VOTING_TOKEN' not defined.", file=STDERR)
        exit(1)

    updater = Updater(
        token=osEnv.get('VOTING_TOKEN'),
        use_context=True
    )

    # Dispatcher
    dp = updater.dispatcher

    # Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_Command),
                      CommandHandler('registrarme', register_Command),
                      CommandHandler('votar', vote_Command)],
        states={},
        fallbacks=[CommandHandler('registrarme', register_Command),
                   CommandHandler('votar', vote_Command)]
    )

    # Handler of the InlineKeyboardButton
    dp.add_handler(CallbackQueryHandler(vote))
    # Added handlers of commands
    dp.add_handler(conv_handler)

    # TODO
    sched.add_job(sendReminder, run_date=VOTING_DATE,)

    # Init DB
    initDB()

    # Starts the bot
    updater.start_polling(clean=True)
    updater.idle()


if __name__ == "__main__":
    main()
