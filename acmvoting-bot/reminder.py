#!/usr/bin/env python

from telegram import Bot

import datetime
from sqlite3 import connect as sql_conn

import msgs
import queries


VOTING_DATE = datetime.datetime.strptime(
    open('election-day', 'r').readline().strip(), "%d/%m/%Y %H:%M")

DB_NAME = 'voters.db'


def read_reg_users():
    conn = sql_conn(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(queries.get_registered_users)
    reg_list = [x[0] for x in cursor.fetchall()]
    conn.close()
    return reg_list


########
# MAIN #
########


def main():

    bot = Bot(token=open('token', 'r').readline().strip())

    for user in read_reg_users():
        bot.send_message(
            chat_id=user,
            text=msgs.reminder.format(time=VOTING_DATE.strftime('%H:%M')),
            parse_mode="html"
        )


if __name__ == "__main__":
    main()
