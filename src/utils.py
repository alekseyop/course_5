import psycopg2
import configparser
import os

def create_or_update_config(file_path):
    config = configparser.ConfigParser()

    if os.path.exists(file_path):
        user_choice = input(f"Файл конфигурации {file_path} уже существует. Хотите пересоздать его? (y/n): ")
        if user_choice.lower() != 'y':
            print("Используется текущий файл конфигурации.")
            return
        else:
            os.remove(file_path)

    dbname = input("Введите имя базы данных(по умолчанию, hh_db_007): ")
    dbname = dbname if dbname else 'hh_db_007'

    user = input("Введите имя пользователя(по умолчанию, postgres): ")
    user = user if user else 'postgres'

    password = input("Введите пароль(по умолчанию, 362362): ")
    password = password if password else '362362'

    host = input("Введите хост(по умолчанию, localhost): ")
    host = host if host else 'localhost'

    port = input("Введите порт(по умолчанию, 5432): ")
    port = port if port else '5432'

    config['postgresql'] = {
        'dbname': dbname,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }

    with open(file_path, 'w') as configfile:
        config.write(configfile)
        print(f"Файл конфигурации {file_path} успешно создан.")


