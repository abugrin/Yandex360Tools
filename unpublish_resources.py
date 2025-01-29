from argparse import ArgumentParser
import argparse
import csv
import logging
import os
import sys
from textwrap import dedent
from time import sleep
import yadisk
from dotenv import load_dotenv
from yadisk.objects import SyncPublicResourceObject, SyncResourceLinkObject
from lib.api360 import API360

load_dotenv()


def logger() -> logging.Logger:
    log_logger = logging.getLogger('UNP')
    log_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    log_file_handler = logging.FileHandler('unpublish_resources.log', encoding='utf8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    log_logger.addHandler(log_handler)
    log_logger.addHandler(log_file_handler)
    return log_logger

log = logger()


def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт УДАЛЯЕТ все настроенные доступы для файлов и папок в диске.
        Параметры:
        --users <file.csv> - файл со списком пользователей. По умолчанию будет использован users.csv
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, required=True, help='Файл со списком пользователей')
    return parser


def read_users_csv(file_path: str) -> list[dict]:
    users:list[dict] = []
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

def main(email: str, unpublish: bool, messenger: bool = False):
    try:
        response = API360.get_service_app_token(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            subject_token=email,
            subject_token_type='urn:yandex:params:oauth:token-type:email'
        )
        if 'error' in response:
            raise Exception(f'{response["error"]}: {response["error_description"]}')

    except Exception as e:
        log.debug(f'User {email} - Failed to get service app token: {e}')

    token = response['access_token']
    # print(token)
    client = yadisk.Client(token=token, session="requests")

    with client:

        if client.check_token():
            log.info(f'User {email} - Test service app token: Success')
        else:
            log.error(f'User {email} - Test service app token: Failed')
            raise Exception('Invalid token for user')

        
        shared_resources: list[SyncPublicResourceObject] = client.get_all_public_resources()

        if unpublish and not messenger:
            log.info(f'Unpublish resources for user: {email}')
            for resource in shared_resources:
                resp: SyncResourceLinkObject = client.unpublish(resource.path)
                log.debug(f'- Unpublish: {resp.path}')
                sleep(0.1)
        elif unpublish and messenger:
            log.info(f'Unpublish resources for user: {email}')
            for resource in shared_resources:
                if 'Файлы Мессенджера' in resource.path:
                    log.debug(f'- Skipping Messenger: {resource.path}')
                    continue
                resp: SyncResourceLinkObject = client.unpublish(resource.path)
                log.debug(f'- Unpublish: {resp.path}')
                sleep(0.1)
        else:
            log.info(f'Listing shared resources for user: {email}')
            for resource in shared_resources:
                log.debug(f'- Shared resource: {resource.path}')


if __name__ == "__main__":
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)

    print(f'Загружено пользователей: {len(users)}')

    print('1) Посмотреть опубликованные ресурсы')
    print('2) !!! УДАЛИТЬ публикацию ВСЕХ ресурсов')
    print('3) !!! УДАЛИТЬ публикацию ВСЕХ ресурсов КРОМЕ Мессенджера')
    print('4) Выход')

    unpublish_choice = input('Выберите: ')


    

    for user in users:
        if user.get('ID')[:3] == "113":
            user_email = user.get('Email')
            try:
                if unpublish_choice == '1':
                    main(email=user_email, unpublish=False)
                elif unpublish_choice == '2':
                    main(email=user_email, unpublish=True)
                elif unpublish_choice == '3':
                    main(email=user_email, unpublish=True, messenger=True)
            except Exception as e:
                log.error(f'User {user_email} - {e}')

    print('Завершено')