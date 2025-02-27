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
    log_logger = logging.getLogger('Deleter')
    log_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    log_file_handler = logging.FileHandler('files_delete.log', encoding='utf8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_logger.addHandler(log_handler)
    log_logger.addHandler(log_file_handler)
    return log_logger

log = logger()

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт удаляет все файлы пользователей из Диска.
        Параметры:
        --users <file.csv> - файл со списком пользователей. По умолчанию будет использован users.csv
        --permanent - при наличии параметра, данные пользователя будут удалены безвозвратно. Иначе перемещены в корзину
        --info - вывести размеры дисков пользователей в файл disk_info.csv
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, required=True, help='CSV файл со списком пользователей')
    parser.add_argument('--permanent', action='store_true', help='Удалить данные безвозвратно')
    parser.add_argument('--info', action='store_true', help='Статистика по дискам пользователей')
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

def delete_user_data(token: str, permanent: bool = False):
    client = yadisk.Client(token=token, session="httpx")

    for item in client.listdir('/'):
        if item['type'] == 'dir':
            log.debug(f'Удаление папки {item["name"]}')
            client.remove(item['path'], permanently=permanent)
        elif item['type'] == 'file':
            log.debug(f'Удаление файла {item["name"]}')
            client.remove(item['path'], permanently=permanent)


def deleter(users: List[Dict], permanent: bool = False):

    print(f'Найдено пользователей: {len(users)}')
    if not permanent:
        print('Данные будут перемещены в корзину')
    else:
        print('Данные будут удалены безвозвратно')
    confirm = input('Вы уверены что хотите удалить данные? (y/n) ')
    if confirm == 'y':
        for user in users:
            user_email = user.get('Email')
            log.debug(f"*** Старт удаления данных для: {user_email}")
            try:
                token = get_service_app_token(user_email)
                delete_user_data(token=token, permanent=permanent)
            except Exception as e:
                log.debug(f"*** Ошибка при удалении данных для: {user_email}")
                log.debug(e)
            log.debug(f"*** Завершено для: {user_email}")
    else:
        exit(0)

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
                
                used_space = round(user_disk_info.used_space / 1024 / 1024, 2)
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
    permanent = args.permanent
    if args.info:
        disk_info(users)
    else:
        deleter(users, permanent)

