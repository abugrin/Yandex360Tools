import argparse
import csv
import logging
import sys
from argparse import ArgumentParser
from logging import Logger
from textwrap import dedent
from typing import List, Dict

import yadisk
from dotenv import load_dotenv

from tools import get_service_app_token

load_dotenv()

def logger() -> Logger:
    log_logger = logging.getLogger('Info')
    log_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    log_file_handler = logging.FileHandler('disk_info.log', encoding='utf8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_logger.addHandler(log_handler)
    log_logger.addHandler(log_file_handler)
    return log_logger

log = logger()

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт сохраняет размеры дисков пользователей в файл disk_info.csv
        Параметры:
        --users <file.csv> - файл со списком пользователей.
        
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, required=True, help='CSV файл со списком пользователей')
    return parser


def read_users_csv(file_path: str) -> List[Dict]:
    users:List[Dict] = []
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row.get('ID')
                if user_id and len(user_id) == 16:
                    users.append(row)
        return users
    except FileNotFoundError:
        print(f'Файл {file_path} не найден')
        exit(1)


def disk_info(users: List[Dict]):
    with open('disk_info.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['ID' , 'Email', 'Size MB'])
        w.writeheader()
        for user in users:
            user_email = user.get('Email')
            log.debug(f"*** Получение информации о диске для: {user_email}")
            try:
                token = get_service_app_token(user_email)
                client: yadisk.Client = yadisk.Client(token=token, session="httpx")
                user_disk_info = client.get_disk_info()
                print()
                used_space = round(user_disk_info.used_space / 1024 / 1024, 0)
                w.writerow({
                        'ID': user.get('ID'),
                        'Email': user_email,
                        'Size MB': used_space
                        })
                log.info(f'{user_email} - {used_space} МБ')
            except Exception as e:
                log.debug(f"*** Ошибка при получении информации о диске для: {user_email}")
                log.debug(e)

if __name__ == "__main__":
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)

    disk_info(users)


