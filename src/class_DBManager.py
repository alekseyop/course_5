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
        create_employers_table_query = """
        CREATE TABLE IF NOT EXISTS employers (
            employer_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255),
            count_vacancies INTEGER
        );
        """
        create_vacancies_table_query = """
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(10) PRIMARY KEY,
            employer_id VARCHAR(10),
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255),
            salary_from INTEGER,
            salary_to INTEGER,
            currency VARCHAR(3),
            FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(create_employers_table_query)
            cursor.execute(create_vacancies_table_query)
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
        print(f'\nЗагружено {len(employer_data)} компаний.')
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

    def get_employer_ids(self):
        """
        Метод извлекает employer_id из таблицы employers
        :return: all employer_id => [employer_id1, employer_id2, ...]

        """
        select_query = "SELECT employer_id FROM employers"
        with self.connection.cursor() as cursor:
            cursor.execute(select_query)
            employer_ids = [row[0] for row in cursor.fetchall()]
        return employer_ids

    def fetch_vacancy_data(self):
        vacancy_data = []
        print('Загружаю данные о вакансиях...')
        count_vacancies = 0
        employer_ids = self.get_employer_ids()
        value_progress_bar = 0
        for employer_id in employer_ids:
            response = requests.get(f'https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=100')
            if response.status_code == 200:
                data = response.json()
                items = data['items']
                if not items:
                    break
                count_vacancies += len(items)
                for item in items:
                    salary = item['salary']
                    salary_from = salary['from'] if salary and salary['from'] else 0
                    salary_to = salary['to'] if salary and salary['to'] else 0
                    currency = salary['currency'] if salary and salary['currency'] else None
                    vacancy_data.append((
                        item['id'], item['employer']['id'], item['name'], item['alternate_url'],
                        salary_from, salary_to, currency
                    ))
            else:
                print(f'Error: {response.status_code} Вакансии не загружены. employer_id = {employer_id}')
                continue
                # break
            value_progress_bar += 1
            print(f'\rЗагружено: {draw_progress_bar(value_progress_bar, len(employer_ids))}', end='')
            self.update_employer_vacancy_count(employer_id, len(items))
        print(f'\nЗагружено {count_vacancies} вакансий.')
        return vacancy_data

    def update_employer_vacancy_count(self, employer_id, count):
        """
        Метод обновляет количество вакансий в таблице employers
        """
        update_query = """
        UPDATE employers
        SET count_vacancies = %s
        WHERE employer_id = %s;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(update_query, (count, employer_id))
            self.connection.commit()


    def insert_vacancy_data(self, vacancy_data):
        """
        Метод добавляет данные о вакансиях в таблицу vacancies
       """
        insert_query = """
        INSERT INTO vacancies (vacancy_id, employer_id, name, url, salary_from, salary_to, currency)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO NOTHING;
        """
        with self.connection.cursor() as cursor:
            cursor.executemany(insert_query, vacancy_data)
            self.connection.commit()

    def close_connection(self):
        """
        Метод закрывает соединение с базой данных
        :return:
        """

        # self.print_select("SELECT * FROM employers;")  # для отладки

        if self.connection:
            self.connection.close()

    def print_select(self, query):
        """
        Метод выводит результаты запроса в виде таблицы
        :param query:
        :return:
        """
        print('\n' + query)
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]

        table = tabulate(results, headers=col_names, tablefmt="psql")
        print(table)

    def get_companies_and_vacancies_count(self):
        """
        Метод получает список всех компаний и количество вакансий у каждой компании
        пункт меню 1
        """
        select_query = """
        SELECT * FROM employers;
        """
        self.print_select(select_query)
        # with self.connection.cursor() as cursor:
        #     cursor.execute(select_query)
        #     result = cursor.fetchall()
        # return result

    def get_all_vacancies(self):
        """
        Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        пункт меню 2
        """
        select_query = """
                SELECT e.name AS company_name,
                    v.name AS vacancy_name,
                    v.salary_from AS salary_from, 
                    v.salary_to AS salary_to, 
                    v.url AS vacancy_url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id;
                """
        self.print_select(select_query)

    def get_avg_salary(self):
        """
        Метод получает среднюю зарплату по вакансиям
        пункт меню 3
        """
        select_query = """
                SELECT AVG(salary_from + salary_to) / 2 AS avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
                """
        self.print_select(select_query)

    def get_vacancies_with_higher_salary(self):
        """
        Метод получает список всех вакансий,
        у которых зарплата выше средней по всем вакансиям
        пункт меню 4
        """
        select_query = """
                WITH avg_salary AS (
                    SELECT AVG(salary_from + salary_to) / 2 AS avg_salary
                    FROM vacancies
                )
                SELECT e.name AS company_name, v.name AS vacancy_name, 
                       v.salary_from AS salary_from, 
                       v.salary_to AS salary_to, 
                       v.url AS vacancy_url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id,
                avg_salary
                WHERE (v.salary_from + v.salary_to) / 2 > avg_salary.avg_salary;
                """
        self.print_select(select_query)

    def get_vacancies_with_keyword(self, word):
        """
        Метод получает список всех вакансий,
        в названии которых содержатся переданные в метод слова
        пункт меню 5
        """
        select_query = f"""
                SELECT e.name AS company_name, v.name AS vacancy_name, 
                       v.salary_from AS salary_from, 
                       v.salary_to AS salary_to, 
                       v.url AS vacancy_url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.name ILIKE '{word}';
                """
        self.print_select(select_query)
