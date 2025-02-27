import csv
import logging
import os
from time import time
from tqdm import tqdm

from dotenv import load_dotenv
from lib.api360 import API360
from lib.disk360 import DiskClient, PublicResourcesList
from tools import get_service_app_token, logger

log: logging.Logger = logger(logger_name = 'DISK', file_name = 'disk_report.log', log_level = logging.INFO, no_console=True)

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


def main():
    api360 = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.INFO)

    client = DiskClient()
    log.info('Загрузка пользователей...')
    users = api360.get_all_users()
    log.info(f'Загрузка пользователей завершена. Загружено {len(users)} пользователей.')
    processed = 0
    with tqdm(total=len(users), unit="User") as progress:
        for user in users:
            if user.uid[:3] == '113':
                log.info(f'Обработка ресурсов пользователя: {user.email}')
                try:
                    token = get_service_app_token(user.email)
                    get_user_shared_resources(user.email, token, client)
                    processed += 1
                
                except Exception as e:
                    log.error(f'Ошибка при обработке ресурсов пользователя: {user.email}')
                    log.error(e)
                    #raise e
            else:
                log.warning(f'Пропуск пользователя: {user.email}')
            progress.update(1)
    client.close()
    return processed, users


if __name__ == '__main__':
    load_dotenv()
    print('Запуск...\n')
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

    processed, users = main()
    
    end_time = time()
    log.info(f'Завершено. Обработано пользователей: {processed} из {len(users)} за {end_time - start_time} секунд.')
    print(f'\nЗавершено. Обработано пользователей: {processed} из {len(users)} за {end_time - start_time} секунд.')
    print('Отчет: disk_report.log')
    print('Результат: disk_report.csv')
    exit(0)