import json
import pathlib
import random
from datetime import datetime, timedelta
from PIL import Image

import prettytable
import pyrogram
from pyrogram.raw import functions

conf = json.load(open("config.json", "r"))

if conf["files"]["file_action"] not in ["remove", "move", "keep"]:
    print("Помилка: неправильно вказано дію з відправленим файлом.")
    conf["files"]["file_action"] = input("keep - залишити; remove - видалити; move - перемістити в окрему папку. ")

if conf["setup"]["date_input_needed"]:
    raw_date = input("Введіть дату (ДД.ММ.РРРР), на яку треба заповнити відкладені"
                     " (натисніть Enter для вибору сьогоднішнього дня): ")

    if raw_date != "":
        date = datetime.strptime(raw_date, "%d.%m.%Y")
    else:
        date = datetime.today()
else:
    date = datetime.today()

days_in_advance = conf["setup"]["days_in_advance"] + 1     # variable context means "how many days to fill in advance", and range() func accepts quantity of elements to iterate over, not end value. That's why I added +1 as magic num.

slots = list()

if conf["setup"]["mode"] == "fixed_interval":
    initial_timestamp = date.timestamp()

    for day_in_advance in range(days_in_advance):
        if date.hour <= int(conf["setup"]["start_hour"]) or day_in_advance >= 1:
            start_date = datetime(date.year, date.month, date.day, int(conf["setup"]["start_hour"])) + timedelta(days=day_in_advance)
        elif date.hour > int(conf["setup"]["start_hour"]):
            start_date = datetime(date.year, date.month, date.day, int(date.hour)) + timedelta(days=day_in_advance)
        else:
            start_date = None

        stop_date = datetime(date.year, date.month, date.day, int(conf["setup"]["stop_hour"])) + timedelta(days=day_in_advance)

        new_initial_timestamp = int(start_date.timestamp())
        interval = conf["setup"]["interval"].split(":")
        interval_timestamp = int(int(interval[0]) * 3600 + int(interval[1]) * 60)

        mod_list = [x for x in range(new_initial_timestamp, int(stop_date.timestamp() + 1), interval_timestamp)]

        for mod in mod_list:
            if mod < int(initial_timestamp) and day_in_advance == 0:
                pass
            else:
                slots.append(mod)

elif conf["setup"]["mode"] == "manual":
    raw_list = conf["timetable"]["manual_slots"]
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

if conf["setup"]["verbose"]:
    print("Список дат:\n")
    [print(datetime.fromtimestamp(ts)) for ts in slots]

if len(slots) >= 100:
    continue_flag = input(f"Перевищено ліміт відкладених повідомлень. Останній запланований пост буде мати дату {datetime.fromtimestamp(slots[100])}. Продовжити чи скасувати (Y/N)? ")
    if continue_flag == "Y" or continue_flag == "y":
        slots = slots[0:100]
    elif continue_flag == "N" or continue_flag == "n":
        exit(1)
    else:
        exit(1)

path_object = pathlib.Path(conf["files"]["path"])
if not path_object.exists():
    print("Шлях не знайдено.")
    exit(1)

accepted_formats = conf["files"]["accepted_formats"]

files = [[unit.stem, unit.suffix] for unit in path_object.iterdir() if
         unit.is_file() and unit.suffix in accepted_formats]
if conf["setup"]["verbose"]:
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

new_folder_object = pathlib.Path(f"{str(path_object)}\\Надіслані")
if not new_folder_object.exists():
    new_folder_object.mkdir()

file_order = random.sample(file_list, len(slots))

if conf["proxy"]["use"]:
    proxy = {
        "scheme": conf["proxy"]["scheme"],
        "hostname": conf["proxy"]["hostname"],
        "port": conf["proxy"]["port"],
        "username": conf["proxy"]["username"],
        "password": conf["proxy"]["password"]
    }
else: proxy = None

if conf["setup"]["use_caption"]:
    with open(conf["files"]["caption_file"]) as cap_file:
        caption = cap_file.read()
else: caption = ""

with pyrogram.Client("sender", api_id=conf["main"]["api_id"], api_hash=conf["main"]["api_hash"], proxy=proxy) as sender:
    for timeslot in slots:
        file_to_send = random.choice(file_order)
        
        if file_to_send.stat().st_size / 1048576 > 5:
            img = Image.open(file_to_send)
            new_path = f'{file_to_send.parents[0]}/{file_to_send.stem}_res{file_to_send.suffix}'
            img.save(new_path,optimize=True,quality=85)
            file_order.remove(file_to_send)
            file_to_send = pathlib.Path(new_path)
            print("Файл було стиснуто.", end=" ")
        else:
            file_order.remove(file_to_send)

        print(f"Файл {file_to_send.name} додано у відкладені, заплановано на {datetime.fromtimestamp(timeslot)}")
        sender.send_photo(conf["main"]["channel_link"], photo=file_to_send, schedule_date=datetime.fromtimestamp(timeslot), caption=caption)

        if conf["files"]["file_action"] == "remove":
            file_to_send.unlink()
        elif conf["files"]["file_action"] == "move":
            file_to_send.rename(f"{str(path_object)}/Надіслані/{file_to_send.name}")
        elif conf["files"]["file_action"] == "keep":
            pass
        else:
            print("Якась незрозуміла хуйня, русскій воєнний корабль йди нахуй!")
            exit(1)

    if len(file_order) == 0:
        print("Всі файли відправлено.")
    else:
            print(f"Не відправлено {len(file_order)} файл(ів), а саме {[file.name for file in file_order if file.is_file()]}")

    request = sender.invoke(functions.messages.GetScheduledHistory(
        peer=sender.resolve_peer(conf["main"]["channel_link"]),
        hash=0))

    with open(conf["files"]["temp_filename"], "w") as temp_file_object:
        print(request, file=temp_file_object)
    with open(conf["files"]["temp_filename"], "r") as temp_file_object:
        data = json.load(temp_file_object)

    with pathlib.Path("./posts.json") as temp_file_pathlib:
        if temp_file_pathlib.exists() and conf["files"]["remove_temp_file"]:
            temp_file_pathlib.unlink()

msg = data["messages"]
checklist = list()

if conf["setup"]["verbose"]:
    print("\nПеревірка черги повідомлень:")

checklist_ts = list()

for message in msg:
    msg_date = datetime.fromtimestamp(message["date"])

    if conf["setup"]["verbose"]:
        print(msg_date)
        checklist.append(msg_date)
