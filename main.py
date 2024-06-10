import os

from config import ROOT_DIR
from src.utils import create_or_update_config, create_db, create_tables


def main():
    file_path = os.path.join(ROOT_DIR, 'config_db.ini')
    create_or_update_config(file_path)
    create_db(file_path)
    create_tables(file_path)



if __name__ == '__main__':
    main()

