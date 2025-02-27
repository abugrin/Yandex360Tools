import csv
import logging
import os
import sys
from lib.api360 import API360

def get_service_app_token(email: str) -> str:
    response = API360.get_service_app_token(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        subject_token=email,
        subject_token_type='urn:yandex:params:oauth:token-type:email'
    )
    if 'error' in response:
        raise Exception(f'Get token error: {response["error"]}: {response["error_description"]}')

    return(response['access_token'])

def logger(logger_name: str, file_name: str, log_level = logging.DEBUG, no_console = False) -> logging.Logger:
    log_logger = logging.getLogger(logger_name)
    log_logger.setLevel(log_level)
    if not no_console:
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s: %(levelname)-8.8s %(message)s'))
        log_logger.addHandler(log_handler)
    log_file_handler = logging.FileHandler(file_name, encoding='utf8')
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s: %(levelname)-8.8s %(message)s'))
    log_logger.addHandler(log_file_handler)
    return log_logger

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