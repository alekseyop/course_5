import psycopg2
import configparser
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_or_update_config(file_path):
    config = configparser.ConfigParser()
    print("Создание и настройка файла конфигурации доступа к базе данных.")
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

    with open(file_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
        print(f"Файл конфигурации {file_path} успешно создан.")


def create_db(file_path):
    """
    Метод создает базу данных
    """
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    dbname = config.get('postgresql', 'dbname')
    user = config.get('postgresql', 'user')
    password = config.get('postgresql', 'password')
    host = config.get('postgresql', 'host')
    port = config.get('postgresql', 'port')

    conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Проверка, существует ли база данных
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
    exists = cur.fetchone()

    if exists:
        # Удаление базы данных, если она существует
        cur.execute(f"DROP DATABASE {dbname}")
        print(f"База данных {dbname} удалена.")

    # Создание новой базы данных
    cur.execute(f"CREATE DATABASE {dbname}")
    print(f"База данных {dbname} создана.")

    # Закрытие соединений
    cur.close()
    conn.close()


def create_tables(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    dbname = config.get('postgresql', 'dbname')
    user = config.get('postgresql', 'user')
    password = config.get('postgresql', 'password')
    host = config.get('postgresql', 'host')
    port = config.get('postgresql', 'port')

    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    # Создание таблиц
    cur.execute('''
    CREATE TABLE IF NOT EXISTS employers (
        employer_id VARCHAR(8) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url VARCHAR(255)
    );
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS vacancies (
        vacancy_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        employer_id VARCHAR(8) NOT NULL,
        url VARCHAR(255),
        salary_from INTEGER,
        salary_to INTEGER,
        currency VARCHAR(3),
        FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
    );
    ''')
    conn.commit()
    cur.close()
    conn.close()


def draw_progress_bar(current: int, total: int, bar_length: int = 30):
    """
    Отображает прогресс загрузки.
    Пример использования: print(f'\rЗагружено: {draw_progress_bar(позиция, количество, end=''}')
    :param current: текущая позиция
    :param total: общее количество
    :param bar_length: длина бара
    :return: строка с прогрессом
    """
    progress = current / total
    num_ticks = int(bar_length * progress)
    bar = '[' + '#' * num_ticks + '_' * (bar_length - num_ticks) + ']'
    percentage = int(progress * 100)
    return f'{bar} {percentage}%'
