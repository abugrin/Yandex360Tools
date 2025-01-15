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
from pathlib import Path
from imapclient import IMAPClient


from dotenv import load_dotenv

from lib.api360 import API360

load_dotenv()

def logger() -> Logger:
    log_logger = logging.getLogger('IMAP')
    log_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    log_file_handler = logging.FileHandler('imap_download.log', encoding='utf8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_logger.addHandler(log_handler)
    log_logger.addHandler(log_file_handler)
    return log_logger

log = logger()

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт скачивает все письма пользователей из Почты в формате EML.
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


async def download_user_mail(token: str, email: str):
    ttl_emails = 0
    with IMAPClient('imap.yandex.ru', ssl=True) as client:
        client.oauth2_login(email, token)
        
        folders = client.list_folders()

        for folder in folders:
            delimiter: bytes
            name: str
            _, delimiter, name = folder

            path = email + "/" + name.replace(delimiter.decode(), '/')
            log.debug(f'Creating directory: {path}')
            Path(path).mkdir(parents=True, exist_ok=True)

            client.select_folder(name)
            messages = client.search(criteria='ALL')
            response = client.fetch(messages, ['RFC822'])

            for msgid, data in response.items():
                with open(Path(path + "/" + str(msgid) + ".eml"), 'wb') as f:
                    f.write(data[b'RFC822'])
                ttl_emails += 1

        log.debug("IPAM connection logout")
        client.logout()

    return ttl_emails

async def get_service_token(user_id: str) -> str:
    response = {}

    try:
        response = await API360.get_service_app_token_async(
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
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)
    print(f'Загружено пользователей: {len(users)}')

    confirm = input('Вы уверены что хотите загрузить письма? (y/n)')

    if confirm == 'y':
        for user in users:
            log.debug(f"*** Старт загрузки писем для: {user.get('Email')}")
            token = await get_service_token(user_id=user.get('ID'))
            emails_processed = await download_user_mail(token=token, email=user.get('Email'))
            log.debug(f"*** Загружено {emails_processed} писем для: {user.get('Email')}")
    else:
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())