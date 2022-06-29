import configparser
import json
import pathlib
import random
from datetime import datetime

import prettytable
import pyrogram
from pyrogram.raw import functions

conf = configparser.ConfigParser()
conf.read("./config.ini")

main_section = dict(conf.items("main"))

json_filename = conf.get("files", "json_filename")

mode = conf.get("setup", "mode")
date_input_needed = conf.getboolean("setup", "date_input_needed")
verbose = conf.getboolean("setup", "verbose")
kebab_action = conf.get("files", "file_action")
remove_temp_file = conf.getboolean("files", "remove_temp_file")

if kebab_action not in ["remove", "move", "keep"]:
    print("Помилка: неправильно вказано дію з відправленим файлом.")
    kebab_action = input("keep - залишити; remove - видалити; move - перемістити в окрему папку. ")

if date_input_needed:
    raw_date = input("Введіть дату (ДД.ММ.РРРР), на яку треба заповнити відкладені"
                     " (натисніть Enter для вибору сьогоднішнього дня): ")

    if raw_date != "":
        date = datetime.strptime(raw_date, "%d.%m.%Y")
    else:
        date = datetime.today()
else:
    date = datetime.today()

start_hour = conf.get("setup", "start_hour")
stop_hour = conf.get("setup", "stop_hour")

slots = list()

if mode == "fixed_interval":
    initial_timestamp = date.timestamp()

    if date.hour <= int(start_hour):
        start_date = datetime(date.year, date.month, date.day, int(start_hour) - 1)
    elif date.hour > int(start_hour):
        start_date = datetime(date.year, date.month, date.day, int(date.hour))
    else:
        start_date = None

    stop_date = datetime(date.year, date.month, date.day, int(stop_hour))

    new_initial_timestamp = int(start_date.timestamp())
    interval = conf.get("setup", "interval").split(":")
    interval_timestamp = int(int(interval[0]) * 3600 + int(interval[1]) * 60)

    mod_list = [x for x in range(new_initial_timestamp, int(stop_date.timestamp() + 1), interval_timestamp)]

    for mod in mod_list:
        if mod < int(initial_timestamp):
            pass
        else:
            slots.append(mod)

elif mode == "manual":
    raw_list = json.loads(conf.get("timetable", "manual_slots"))
    cooked_list = list()
    for i in raw_list:
        cooked_list.append(tuple(i.split(":")))

    for slot in cooked_list:
        datetime_obj = datetime(date.year, date.month, date.day, int(slot[0]), int(slot[1]))
        slots.append(datetime_obj.timestamp())
else:
    print("Вибрано непідтримуваний режим роботи.")
    exit(1)

if verbose:
    print("Список дат:\n")
    [print(datetime.fromtimestamp(ts)) for ts in slots]

path_object = pathlib.Path(conf.get("files", "path"))
if not path_object.exists():
    print("Шлях не знайдено.")
    exit(1)

accepted_formats = json.loads(conf.get("files", "accepted_formats"))

files = [[unit.stem, unit.suffix] for unit in path_object.iterdir() if
         unit.is_file() and unit.suffix in accepted_formats]
if verbose:
    table = prettytable.PrettyTable()
    table.field_names = ["Ім'я", "Розширення"]

    for file in files:
        table.add_row(file)

    table.align["Ім\"я"] = "l"
    print(table)

file_list = [unit for unit in path_object.iterdir() if unit.is_file()]

if len(files) < len(slots):
    print("Недостатньо файлів для заповнення черги.")
    exit(1)

new_folder_object = pathlib.WindowsPath(f"{str(path_object)}\\Надіслані")
if not new_folder_object.exists():
    new_folder_object.mkdir()

file_order = random.sample(file_list, len(slots))

with pyrogram.Client("sender", api_id=main_section["api_id"], api_hash=main_section["api_hash"]) as sender:
    for timeslot in slots:
        file_to_send = random.choice(file_order)
        file_order.remove(file_to_send)
        print(f"Файл {file_to_send.name} додано у відкладені, заплановано на {datetime.fromtimestamp(timeslot)}")
        sender.send_photo(main_section["channel_link"], photo=file_to_send, schedule_date=int(timeslot))

        if kebab_action == "remove":
            file_to_send.unlink()
        elif kebab_action == "move":
            file_to_send.rename(f"{str(path_object)}/Надіслані/{file_to_send.name}")
        elif kebab_action == "keep":
            pass
        else:
            print("Якась незрозуміла хуйня, русскій воєнний корабль йди нахуй!")
            exit(1)

if len(file_order) == 0:
    print("Всі файли відправлено.")
else:
    print(f"Не відправлено {len(file_order)} файл(ів), а саме {[file.name for file in file_order if file.is_file()]}")

sender.start()
request = sender.send(functions.messages.GetScheduledHistory(
    peer=sender.resolve_peer(main_section["channel_link"]),
    hash=0))

with open(json_filename, "w") as temp_file_object:
    print(request, file=temp_file_object)
with open(json_filename, "r") as temp_file_object:
    data = json.load(temp_file_object)

with pathlib.Path("./posts.json") as temp_file_pathlib:
    if temp_file_pathlib.exists() and remove_temp_file:
        temp_file_pathlib.unlink()

msg = data["messages"]
checklist = list()

if verbose:
    print("\nПеревірка черги повідомлень:")

checklist_ts = list()

for message in msg:
    msg_date = datetime.fromtimestamp(message["date"])

    if verbose:
        print(msg_date)
        checklist.append(msg_date)
