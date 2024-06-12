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
    db_manager.close_connection()



if __name__ == '__main__':
    main()

