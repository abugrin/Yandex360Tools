import argparse
import asyncio
import csv
import logging
import os
import sys
import caldav
from argparse import ArgumentParser
from logging import Logger
from textwrap import dedent
from typing import List, Dict


from dotenv import load_dotenv

from lib.api360 import API360

load_dotenv()

def logger() -> Logger:
    log_logger = logging.getLogger('IMAP')
    log_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    log_file_handler = logging.FileHandler('caldav_delete.log', encoding='utf8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_logger.addHandler(log_handler)
    log_logger.addHandler(log_file_handler)
    return log_logger

log = logger()

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт УДАЛЯЕТ все календари пользователей.
        Параметры:
        --users <file.csv> - файл со списком пользователей. По умолчанию будет использован users.csv
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, default='users.csv', help='Файл со списком пользователей')
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


async def delete_user_calendar(token: str, email: str):
    ttl_calendars = 0

    with caldav.DAVClient(url="https://caldav.yandex.ru/", username=email, password=token) as client:
        principal = client.principal()
        calendars = principal.calendars()
        for calendar in calendars:
            try:
                log.debug(f'Deleting calendar: {calendar.name}')
                calendar.delete()
                ttl_calendars += 1
            except Exception as e:
                log.debug(f'Failed to delete calendar: {e}')
                        
    return ttl_calendars

async def get_service_token(api: API360, user_id: str) -> str:
    response = {}

    try:
        response = await api.get_service_app_token(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            subject_token=user_id,
            subject_token_type='urn:yandex:params:oauth:token-type:uid'
        )
    except Exception as e:
        log.debug(f'Failed to get service app token: {e}')
        exit(1)
    return response['access_token']


async def main():
    api360 = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.DEBUG)
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)
    print(f'Загружено пользователей: {len(users)}')

    confirm = input('Вы уверены что хотите УДАЛИТЬ календари? (y/n)')

    if confirm == 'y':
        for user in users:
            log.debug(f"*** Старт удаления календарей для: {user.get('Email')}")
            token = await get_service_token(api=api360, user_id=user.get('ID'))
            calendars_processed = await delete_user_calendar(token=token, email=user.get('Email'))
            log.debug(f"*** Удалено {calendars_processed} календарей для: {user.get('Email')}")
    else:
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())