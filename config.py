import configparser
from data import *


def write_config(config_name):
    with open(config_name, 'w') as conf_file:
        conf.write(conf_file)
        print("Зміни записано.")


conf = configparser.ConfigParser()
conf_name = input("Введіть назву файлу конфігурації: ")
conf.read(conf_name)

conf_items = [dict(conf.items(x)) for x in conf.sections()]

if not conf_items:
    create_conf = input("Файл конфігурації пустий або не існує. Створити новий? (y/n) ")
    edit_conf = "n"
else:
    edit_conf = input("Файл не пустий. Перейти до редагування? (y/n) ")
    create_conf = "n"

if create_conf == "n" and edit_conf == "n":
    exit()

elif create_conf == "n" and edit_conf == "y":
    while True:
        action = input("\nВиберіть дію:\n\tlist - перелік значень та описів\n\t"
                       "val - поточні значення\n\t"
                       "edit - редагування значення\n\t"
                       "exit - закінчити, зберегти зміни та вийти\n?: ")

        if action == 'exit':
            write_config(conf_name)
            exit()

        elif action == 'val':
            print('\n')
            read_values = dict()
            for item in list(conf.items()):
                section = conf.items(item[0])
                read_values.update(section)
            [print(key, '=', value) for key, value in read_values.items()]

        elif action == 'list':
            for param in descriptions.keys():
                print(f'{param} - {descriptions[param]}')

        elif action == "edit":
            new_section = input("Секція, в якій знаходиться значення: ")
            value_to_change = input("Значення, яке потрібно змінити: ")
            if value_to_change in descriptions.keys():
                new_value = input("Нове значення: ")
                conf.set(new_section, value_to_change, new_value)


elif create_conf == 'y' and edit_conf == "n":
    for value_key in values.keys():
        if value_key in bool_parameters:
            values[value_key] = input(f'{value_key} - {descriptions[value_key]} (on/off): ')

        elif value_key in list_parameters:
            emerge_list = list()
            print("\nКожне значення в новому рядку, для виходу - натисніть Enter.\n")
            new_val = "Non-empty value"

            while True:
                new_val = input(f'{value_key} - {descriptions[value_key]}: ')
                if new_val == '':
                    break

                emerge_list.append(new_val)
                values[value_key] = str(emerge_list)
        else:
            values[value_key] = input(f'{value_key} - {descriptions[value_key]}: ')

    for key in conf_params.keys():
        conf.add_section(key)
        for parameter in conf_params[key]:
            conf.set(key, parameter, values[parameter])

    write_config(conf_name)
