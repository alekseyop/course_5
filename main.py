import os

from config import ROOT_DIR
from src.class_DBManager import DBManager
from src.utils import create_or_update_config, create_db


def main():
    file_path = os.path.join(ROOT_DIR, 'config_db.ini')
    create_or_update_config(file_path)
    create_db(file_path)
    db_manager = DBManager()
    db_manager.create_table()
    employer_data = db_manager.fetch_employer_data()
    db_manager.insert_employer_data(employer_data)
    vacancy_data = db_manager.fetch_vacancy_data()
    db_manager.insert_vacancy_data(vacancy_data)

    while True:
        print('1 - получает список всех компаний и количество вакансий у каждой компании.\n'
              '2 - получает список всех вакансий с указанием названия компании,\n'
              '    названия вакансии и зарплаты и ссылки на вакансию.\n'
              '3 - получает среднюю зарплату по вакансиям\n'
              '4 - получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.\n'
              '5 - получает список всех вакансий,\n'
              '    в названии которых содержатся переданные в метод слова, например python.\n'
              '0 - завершает работу.\n')
        action = input()
        if action == '1':
            db_manager.get_companies_and_vacancies_count()

        elif action == '2':
            db_manager.get_all_vacancies()

        elif action == '3':
            db_manager.get_avg_salary()

        elif action == '4':
            db_manager.get_vacancies_with_higher_salary()

        elif action == '5':
            word = input('Введите слово: ')
            db_manager.get_vacancies_with_keyword(word)
        else:
            db_manager.close_connection()
            exit()


if __name__ == '__main__':
    main()
