class DBManager:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

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
