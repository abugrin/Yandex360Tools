import argparse
import csv
import logging
import os
import sys
from argparse import ArgumentParser
from logging import Logger
from textwrap import dedent
from typing import List, Dict
from imapclient import IMAPClient


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
        Скрипт УДАЛЯЕТ все письма пользователей из Почты.
        Параметры:
        --users <file.csv> - файл со списком пользователей. По умолчанию будет использован users.csv
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


def delete_user_mail(token: str, email: str):
    ttl_emails = 0
    chunk_size = 1000

    with IMAPClient('imap.yandex.ru', ssl=True) as client:
        client.oauth2_login(email, token)
        
        folders = client.list_folders()

        for folder in folders:
            _, _, name = folder
            
            client.select_folder(name)
            messages = client.search(criteria='ALL')
            log.debug(f"Обработка папки: {name} - Количество сообщений: {len(messages)}")

            messages_split = list(split_list_into_chunks(messages, chunk_size))
            
            for i, messages_chunk in enumerate(messages_split):
                #print(f"Chunk {i + 1}: {messages_chunk}")
                deleted = client.delete_messages(messages_chunk)
                ttl_emails += len(deleted)


        log.debug("IMAP expunge")
        client.expunge()
        log.debug("IMAP connection logout")
        client.logout()

    return ttl_emails

def split_list_into_chunks(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]



def get_service_token(user_id: str) -> str:
    response = {}

    try:
        response = API360.get_service_app_token(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            subject_token=user_id,
            subject_token_type='urn:yandex:params:oauth:token-type:uid'
        )
    except Exception as e:
        log.debug(f'Failed to get service app token: {e}')
        exit(1)
    return response['access_token']


def main():
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)
    print(f'Загружено пользователей: {len(users)}')

    confirm = input('Вы уверены что хотите УДАЛИТЬ письма? (y/n)')

    if confirm == 'y':
        for user in users:
            log.debug(f"*** Старт удаления писем для: {user.get('Email')}")
            token = get_service_token(user_id=user.get('ID'))
            emails_processed = delete_user_mail(token=token, email=user.get('Email'))
            log.debug(f"*** Удалено {emails_processed} писем для: {user.get('Email')}")
    else:
        exit(0)


if __name__ == "__main__":
    main()