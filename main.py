import configparser
import json
import pathlib
import random
from datetime import datetime
from click import password_option

import prettytable
import pyrogram
from pyrogram.raw import functions
from zmq import proxy

conf = configparser.ConfigParser()
conf.read("./config.ini")

main_section = dict(conf.items("main"))

json_filename = conf.get("files", "json_filename")

mode = conf.get("setup", "mode")
date_input_needed = conf.getboolean("setup", "date_input_needed")
verbose = conf.getboolean("setup", "verbose")
kebab_action = conf.get("files", "file_action")
remove_temp_file = conf.getboolean("files", "remove_temp_file")

proxy_use = conf.getboolean("proxy", "use")
proxy_scheme = conf.get("proxy", "scheme")
proxy_hostname = conf.get("proxy", "hostname")
proxy_port = int(conf.get("proxy", "port"))
proxy_username = conf.get("proxy", "username")
proxy_password = conf.get("proxy", "password")

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
days_in_advance = int(conf.get("setup", "days_in_advance")) + 1     # variable context means "how many days to fill in advance", and range() func accepts quantity of elements to iterate over, not end value. That's why I added +1 as magic num.

slots = list()

if mode == "fixed_interval":
    initial_timestamp = date.timestamp()

    for day_in_advance in range(days_in_advance):
        if date.hour <= int(start_hour) or day_in_advance >= 1:
            start_date = datetime(date.year, date.month, date.day + day_in_advance, int(start_hour))
        elif date.hour > int(start_hour):
            start_date = datetime(date.year, date.month, date.day + day_in_advance, int(date.hour))
        else:
            start_date = None

        stop_date = datetime(date.year, date.month, date.day + day_in_advance, int(stop_hour))

        new_initial_timestamp = int(start_date.timestamp())
        interval = conf.get("setup", "interval").split(":")
        interval_timestamp = int(int(interval[0]) * 3600 + int(interval[1]) * 60)

        mod_list = [x for x in range(new_initial_timestamp, int(stop_date.timestamp() + 1), interval_timestamp)]

        for mod in mod_list:
            if mod < int(initial_timestamp) and day_in_advance == 0:
                pass
            else:
                slots.append(mod)

elif mode == "manual":
    raw_list = json.loads(conf.get("timetable", "manual_slots"))
    cooked_list = list()
    for i in raw_list:
        cooked_list.append(tuple(i.split(":")))

    for day_in_advance in range(days_in_advance):
        for slot in cooked_list:
            datetime_obj = datetime(date.year, date.month, date.day, int(slot[0]), int(slot[1]))
            if int(datetime_obj.timestamp()) <= int(date.timestamp()) and day_in_advance == 0:
                pass
            else:
                slots.append(int(datetime_obj.timestamp()))
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

if proxy_use:
    proxy = {
        "scheme": proxy_scheme,
        "hostname": proxy_hostname,
        "port": proxy_port,
        "username": proxy_username,
        "password": proxy_password
    }
else: proxy = None

with pyrogram.Client("sender", api_id=main_section["api_id"], api_hash=main_section["api_hash"], proxy=proxy) as sender:
    for timeslot in slots:
        file_to_send = random.choice(file_order)
        file_order.remove(file_to_send)
        print(f"Файл {file_to_send.name} додано у відкладені, заплановано на {datetime.fromtimestamp(timeslot)}")
        sender.send_photo(main_section["channel_link"], photo=file_to_send, schedule_date=datetime.fromtimestamp(timeslot))

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

    request = sender.invoke(functions.messages.GetScheduledHistory(
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
