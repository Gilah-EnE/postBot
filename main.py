import datetime

import pyrogram
import configparser
import random

config = configparser.ConfigParser()
config.read("config.ini")

timetable_minutes = config.get('timetable', 'minutes')

hour = 0
slots = []
timestamps = []
nowtime = datetime.datetime.now()

for timetable_minute in timetable_minutes:
    slots.append(f'{str(nowtime.day).zfill(2)}.{str(nowtime.month).zfill(2)}.{str(nowtime.year).zfill(4)}'
                 f'{str(hour).zfill(2)}:{str(timetable_minute).zfill(2)}')
    hour += 1

for slot in slots:
    timestamps.append(datetime.datetime.strptime(slot, "%d.%m.%Y %H:%M").timestamp())

bot_id = config.get('api', 'api_id')
bot_hash = config.get('api', 'api_hash')

with pyrogram.Client("my_account", bot_id, bot_hash) as app:
    app.send_message("me", "Greetings from **Pyrogram**!")
