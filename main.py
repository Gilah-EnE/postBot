import datetime
import os
import random
import configparser
import json
import glob

import pyrogram

config = configparser.ConfigParser()
config.read("config.ini")

bot_id = config.get('api', 'api_id')
bot_hash = config.get('api', 'api_hash')

timetable_minutes = json.loads(config.get('timetable', 'minutes'))

slots = []
timestamps = []
nowtime = datetime.datetime.now()
hour = nowtime.hour

for timetable_minute in timetable_minutes:
    slots.append(f'{str(nowtime.day).zfill(2)}.{str(nowtime.month).zfill(2)}.{str(nowtime.year).zfill(4)} '
                 f'{str(hour).zfill(2)}:{str(timetable_minute).zfill(2)}')
    hour += 1
    if hour >= 24:
        break

for slot in slots:
    timestamps.append(datetime.datetime.strptime(slot, "%d.%m.%Y %H:%M").timestamp())

with pyrogram.Client("my_account", bot_id, bot_hash) as app:
    # app.send_message("me", "Greetings from **Pyrogram**!")
    for time in timestamps:
        picture = os.path.relpath(random.choice(glob.glob('./*.jpg')))
        app.send_photo(config.get('channel', 'channel_link'), picture, schedule_date=int(time))
        print(f'Sent {picture}, scheduled at {datetime.datetime.fromtimestamp(time)}')
        # os.remove(picture)
