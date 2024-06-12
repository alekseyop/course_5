import configparser
import psycopg2
import requests

from tabulate import tabulate
from config import EMPLOYER_IDS
from src.utils import draw_progress_bar


class DBManager:
    def __init__(self, config_file='config_db.ini'):
        self.config = self.read_config(config_file)
        self.connection = self.connect_db()

    def read_config(self, filename):
        parser = configparser.ConfigParser()
        parser.read(filename)
        return parser['postgresql']

    def connect_db(self):
        conn = psycopg2.connect(
            dbname=self.config['dbname'],
            user=self.config['user'],
            password=self.config['password'],
            host=self.config['host'],
            port=self.config['port']
        )
        return conn

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS employers (
            employer_id VARCHAR(8) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255),
            count_vacancies INTEGER
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(create_table_query)
            self.connection.commit()

    def fetch_employer_data(self):
        employer_data = []
        print('Загружаю данные о компаниях...')
        for employer_id in EMPLOYER_IDS:
            response = requests.get(f'https://api.hh.ru/employers/{employer_id}')
            if response.status_code == 200:
                data = response.json()
                employer_data.append((data['id'], data['name'], data['alternate_url'], int(data['open_vacancies'])))
                print(f'\rЗагружено: {draw_progress_bar(len(employer_data), len(EMPLOYER_IDS))}', end='')
        return employer_data

    def insert_employer_data(self, employer_data):
        """
        Метод добавляет данные о компаниях в таблицу employers
        :param employer_data:
        :return:
        """
        insert_query = """
        INSERT INTO employers (employer_id, name, url, count_vacancies)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (employer_id) DO NOTHING;
        """
        with self.connection.cursor() as cursor:
            cursor.executemany(insert_query, employer_data)
            self.connection.commit()

    def close_connection(self):
        """
        Метод закрывает соединение с базой данных
        :return:
        """

        self.print_select("SELECT * FROM employers;")  # для отладки

        if self.connection:
            self.connection.close()

    def print_select(self, query):
        """
        Метод выводит результаты запроса в виде таблицы
        :param query:
        :return:
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]

        table = tabulate(results, headers=colnames, tablefmt="psql")
        print('\n' + table)

    def get_companies_and_vacancies_count(self):
        """
        Метод получает список всех компаний и количество вакансий у каждой компании
        """
        pass

    def get_all_vacancies(self):
        """
        Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        """
        pass

    def get_avg_salary(self):
        """
        Метод получает среднюю зарплату по вакансиям
        """
        pass

    def get_vacancies_with_higher_salary(self):
        """
        Метод получает список всех вакансий,
        у которых зарплата выше средней по всем вакансиям
        """
        pass

    def get_vacancies_with_keyword(self, word):
        """
        Метод получает список всех вакансий,
        в названии которых содержатся переданные в метод слова
        """
        pass
