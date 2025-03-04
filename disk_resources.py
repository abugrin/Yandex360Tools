from argparse import ArgumentParser
import argparse
import csv
import logging
from textwrap import dedent
from time import time
from typing import Dict, List
from tqdm import tqdm

from dotenv import load_dotenv
from lib.disk360 import DiskClient, PublicResourcesList
from tools import get_service_app_token, logger

log: logging.Logger = logger(logger_name = 'DISK', file_name = 'disk_report.log', log_level = logging.INFO, no_console=True)

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт выгружает данные о ресурсах на диске, которыми поделился пользователь в файл disk_report.csv
        Параметры:
        --users <file.csv> - файл со списком пользователей.
        
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, required=True, help='CSV файл со списком пользователей')
    return parser

def get_user_shared_resources(email: str, token: str, client: DiskClient):

    resources_list: PublicResourcesList = client.get_public_resources(token=token, limit=100, offset=0)

    resource_items = resources_list.items
    with open('disk_report.csv', 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['email',
                               'path',
                               'access_type',
                               'rights',
                               'user_id',
                               'external_user'])
        
        for resource in resource_items:

            log.debug(f'*** Ресурс {resource.type}: {resource.name} путь: {resource.path}')
            
            resource_path = resource.path[5:]
            res = client.get_public_settings(token, resource_path)
            accesses = res.public_accesses
            for access in accesses:
                if access.access_type == 'macro':
                    if access.macros == 'all':
                        log.debug(f"Есть внешний доступ! Права: {access.rights}")
                        w.writerow({
                            'email': email,
                            'path': resource_path,
                            'access_type': 'public',
                            'rights': access.rights,
                            'user_id': '',
                            'external_user': ''

                        })
                    elif access.macros == 'employees':
                        log.debug(f"Только внутри компании. Права: {access.rights}")
                        w.writerow({
                            'email': email,
                            'path': resource_path,
                            'access_type': 'employees',
                            'rights': access.rights,
                            'user_id': '',
                            'external_user': ''
                        })
                elif access.access_type == 'user':
                    log.debug(f"Доступ сотруднику: {access.user_id} права: {access.rights}")
                    w.writerow({
                        'email': email,
                        'path': resource_path,
                        'access_type': 'user',
                        'rights': access.rights,
                        'user_id': access.user_id,
                        'external_user': not access.org_id
                    })
                else:
                    log.debug(f"Другой доступ: {access}")
                    w.writerow({
                        'email': email,
                        'path': resource_path,
                        'access_type': access.access_type,
                        'rights': access.rights,
                        'user_id': access.user_id,
                        'external_user': not access.org_id,
                        
                    })


def main(users: List[Dict]):
    client = DiskClient()
    log.info('Загрузка пользователей...')

    log.info(f'Загрузка пользователей завершена. Загружено {len(users)} пользователей.')
    processed = 0
    with tqdm(total=len(users), unit="User") as progress:
        for user in users:
            if user.get('ID')[:3] == '113':
                user_email = user.get('Email')
                log.info(f'Обработка ресурсов пользователя: {user_email}')
                try:
                    token = get_service_app_token(user_email)
                    get_user_shared_resources(user_email, token, client)
                    processed += 1
                
                except Exception as e:
                    log.error(f'Ошибка при обработке ресурсов пользователя: {user_email}')
                    log.error(e)
                    #raise e
            else:
                log.warning(f'Пропуск пользователя: {user_email}')
            progress.update(1)
    client.close()
    return processed, users


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

if __name__ == '__main__':
    load_dotenv()
    print('Запуск...\n')
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)
    
    start_time = time()

    with open('disk_report.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['email',
                               'path',
                               'access_type',
                               'rights',
                               'user_id',
                               'external_user'
                               ])
        w.writeheader()    

    processed, users = main(users=users)
    
    end_time = time()
    log.info(f'Завершено. Обработано пользователей: {processed} из {len(users)} за {end_time - start_time} секунд.')
    print(f'\nЗавершено. Обработано пользователей: {processed} из {len(users)} за {end_time - start_time} секунд.')
    print('Отчет: disk_report.log')
    print('Результат: disk_report.csv')
    exit(0)