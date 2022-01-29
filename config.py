import configparser
import random

import prettytable

user_id = input('Enter api_id: ')
user_hash = input('Enter api_hash: ')

config = configparser.ConfigParser()

config['api'] = {'api_id': user_id, 'api_hash': user_hash}

posts_per_hour = int(input("How many posts per hour: "))

config['timetable'] = {'minutes': random.sample(range(0, 59), (23 * posts_per_hour))}

link = input('Enter channel link (public only): ')

config['channel'] = {'channel_link': link}

table = prettytable.PrettyTable()

table.field_names = ['user_id', 'user_hash', 'posts_per_hour', 'channel_link']
table.add_row([user_id, user_hash, posts_per_hour, link])

print(config.get('timetable', 'minutes'))

with open('config.ini', 'w') as conffile:
    config.write(conffile)

print(table)
