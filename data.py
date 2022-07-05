conf_params = {'main': ['api_id', 'api_hash', 'channel_link'],
               'setup': ['mode', 'start_hour', 'stop_hour', 'interval', 'date_input_needed', 'verbose'],
               'timetable': ['manual_slots'],
               'files': ['path', 'accepted_formats', 'file_action', 'json_filename', 'remove_temp_file']}

values = {'api_id': '', 'api_hash': '', 'channel_link': '', 'mode': '',
          'start_hour': '', 'stop_hour': '', 'interval': '', 'date_input_needed': '', 'verbose': '',
          'manual_slots': '',
          'path': '', 'accepted_formats': '', 'file_action': '', 'json_filename': '', 'remove_temp_file': ''}

descriptions = {'api_id': '[main] Отримати на my.telegram.org',
                'api_hash': '[main] Отримати на my.telegram.org',
                'channel_link': '[main] Посилання на канал (без @)',
                'mode': '[setup] Режим роботи бота (manual/fixed_interval)',
                'start_hour': '[setup] Для mode = fixed_interval, година для початку заповнення черги',
                'stop_hour': '[setup] Для mode = fixed_interval, година для кінця заповнення черги',
                'interval': '[setup] Для mode = fixed_interval, інтервал заповнення черги',
                'date_input_needed': '[setup] Запитувати введення дати (якщо ні, при запуску вибереться сьогоднішня '
                                     'дата)',
                'verbose': '[setup] Режим виведення додаткової інформації',
                'manual_slots': '[timetable] Для mode=manual, список слотів',
                'path': '[files] Шлях до папки з артами',
                'accepted_formats': '[files] Формати файлів, які можна надсилати',
                'file_action': '[files] Дія з файлом після надсилання (move/remove/keep) ('
                               'перемістити/видалити/залишити)',
                'json_filename': '[files] Назва тимчасового файлу формату JSON',
                'remove_temp_file': '[files] Видаляти тимчасовий файл?'
                }

bool_parameters = ['date_input_needed', 'verbose', 'remove_temp_file']
list_parameters = ['manual_slots', 'accepted_formats']