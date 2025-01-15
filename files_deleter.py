import argparse
import asyncio
import csv
import logging
import os
import sys
from argparse import ArgumentParser
from logging import Logger
from textwrap import dedent
from typing import List, Dict

import yadisk
from dotenv import load_dotenv

from lib.api360 import API360

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
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, default='users.csv', help='Файл со списком пользователей')
    parser.add_argument('--permanent', action='store_true', help='Удалить данные безвозвратно')
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

async def delete_user_data(token: str, permanent: bool = False):
    client = yadisk.AsyncClient(token=token)

    async for item in client.listdir('/'):
        if item['type'] == 'dir':
            log.debug(f'Удаление папки {item["name"]}')
            await client.remove(item['path'], permanently=permanent)
        elif item['type'] == 'file':
            log.debug(f'Удаление файла {item["name"]}')
            await client.remove(item['path'], permanently=permanent)



async def get_service_token(api: API360, user_id: str) -> str:
    response = {}
    try:
        try:
            response = await api.get_service_app_token_async(
                client_id=os.getenv('CLIENT_ID'),
                client_secret=os.getenv('CLIENT_SECRET'),
                subject_token=user_id,
                subject_token_type='urn:yandex:params:oauth:token-type:uid'
            )
        except Exception as e:
            log.debug(f'Failed to get service app token: {e}')
            exit(1)
        return response['access_token']
    except Exception as e:
        log.debug(f'Failed to connect to API: {e}, response: {response}')
        exit(1)

async def main():
    api360 = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.DEBUG)
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)
    permanent = args.permanent
    print(f'Найдено пользователей: {len(users)}')
    if not permanent:
        print('Данные будут перемещены в корзину')
    else:
        print('Данные будут удалены безвозвратно')
    confirm = input('Вы уверены что хотите удалить данные? (y/n)')
    if confirm == 'y':
        for user in users:
            log.debug(f"*** Старт удаления данных для: {user.get('Email')}")
            token = await get_service_token(api=api360, user_id=user.get('ID'))
            await delete_user_data(token=token, permanent=permanent)
            log.debug(f"*** Завершено для: {user.get('Email')}")
    else:
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())
