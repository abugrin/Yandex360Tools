import argparse
import asyncio
import csv
import enum
import logging
import os
import sys
import imaplib
from argparse import ArgumentParser
from logging import Logger
from textwrap import dedent
from typing import List, Dict, Optional

from dotenv import load_dotenv

from lib.api360 import API360

load_dotenv()

def logger() -> Logger:
    log_logger = logging.getLogger('IMAP')
    log_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    log_file_handler = logging.FileHandler('imap_delete.log', encoding='utf8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_logger.addHandler(log_handler)
    log_logger.addHandler(log_file_handler)
    return log_logger

log = logger()

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт удаляет все письма пользователей из Почты.
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

def generate_oauth2_string(username, access_token):
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
    return auth_string

def get_imap_connector(username, token):
    auth_string = generate_oauth2_string(username, token)
    imap_connector = imaplib.IMAP4_SSL("imap.yandex.ru", 993)
    imap_connector.authenticate('XOAUTH2', lambda x: auth_string)
    return imap_connector

def map_folder(folder: Optional[bytes]) -> Optional[str]:
    if not folder or folder == b"LIST Completed.":
        return None
    valid = folder.decode("ascii").split('"|"')[-1].strip().strip('""')
    return f'"{valid}"'

def process_emails(imap_connector: imaplib.IMAP4_SSL):
    ttl_emails = 0
    status, folders = imap_connector.list('""', "*")
    folders = [map_folder(folder) for folder in folders if map_folder(folder)]

    for folder in folders:
        
        log.debug(f"Processing Folder: {folder}")
        try:
            imap_connector.select(folder)
            status, data = imap_connector.search(None, 'ALL')
            log.debug(f"Search folder {folder} Response: {status}")
            # log.debug(f"Reading folder {folder} Data: {data[0]}")
            for num in data[0].split(b' '):
                if num == b'':
                    continue
                imap_connector.store(num, '+FLAGS', '\\Deleted')
                ttl_emails += 1
            
        except imaplib.IMAP4.error as e:
            log.debug(f"Folder: {folder} IMAP4 error: ", e)
        except ValueError as e:
            log.debug(f"Folder: {folder} Value error: ", e)
        log.debug(f"Folder: {folder} delete complete.")

    log.debug("IPAM connection expunge")
    imap_connector.expunge()
    log.debug("IPAM connection close")
    imap_connector.close()
    log.debug("IPAM connection logout")
    imap_connector.logout()

    return ttl_emails


async def delete_user_mail(token: str, email: str):
    imap_connector = get_imap_connector(username=email, token=token)
    return(process_emails(imap_connector))


async def get_service_token(api: API360, user_id: str) -> str:
    response = {}
    try:
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
    except Exception as e:
        log.debug(f'Failed to connect to API: {e}, response: {response}')
        exit(1)

async def main():
    api360 = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.DEBUG)
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)
    print(f'Найдено пользователей: {len(users)}')

    confirm = input('Вы уверены что хотите удалить письма? (y/n)')

    if confirm == 'y':
        for user in users:
            log.debug(f"*** Старт удаления писем для: {user.get('Email')}")
            token = await get_service_token(api=api360, user_id=user.get('ID'))
            emails_processed = await delete_user_mail(token=token, email=user.get('Email'))
            log.debug(f"*** Удалено {emails_processed} писем для: {user.get('Email')}")
    else:
        exit(0)


class DeletionStatus(enum.Enum):
    NotFound = "Not Found"
    Empty = "Empty"
    Deleted = "Deleted"


if __name__ == "__main__":
    asyncio.run(main())