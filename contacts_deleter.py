
from argparse import ArgumentParser
import argparse
from textwrap import dedent
import time
from dotenv import load_dotenv
import requests

from tools import get_service_app_token, logger, read_users_csv

load_dotenv()

log = logger('CONTACTS', 'contacts_deleter.log')

def arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=dedent("""
        Скрипт УДАЛЯЕТ все личные контакты пользователя по списку.
        Параметры:
        --users <file.csv> - файл со списком пользователей.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--users', type=str, required=True, help='Файл со списком пользователей')
    return parser

def read_contacts(email: str):
    token = get_service_app_token(email)

    session = requests.Session()
    session.auth = (email, token)

    response = session.get(f'https://carddav.yandex.ru/addressbook/{email}/1/?op=ls')
    contacts_list = response.json().get('list')


    for contact in contacts_list:
        file_name = contact.get('fileName')
        log.debug(f'Контакт: {file_name} tag: {contact.get('etag')}')
        #contact_data = response = session.get(f'https://carddav.yandex.ru/addressbook/{email}/1/{file_name}')
        #log.debug(contact_data.text)
        time.sleep(0.1)

def delete_contacts(email: str):
    token = get_service_app_token(email)

    session = requests.Session()
    session.auth = (email, token)

    response = session.get(f'https://carddav.yandex.ru/addressbook/{email}/1/?op=ls')

    contacts_list = response.json().get('list')

    for contact in contacts_list:
        file_name = contact.get('fileName')
        log.debug(f'Удаление: {file_name} tag: {contact.get('etag')}')
        response = session.delete(f'https://carddav.yandex.ru/addressbook/{email}/1/{file_name}')
        time.sleep(0.1)


if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    users = read_users_csv(args.users)

    print('1) Посмотреть список личных контактов')
    print('2) Удалить все личные контакты')
    print('3) Выход')

    choice = input('Выберите действие: ')

    for user in users:
        email = user.get('Email')
        if email:
            
            if choice == '1':
                log.debug(f'Контакты пользователя: {email}')
                read_contacts(email)
            elif choice == '2':
                log.debug(f'Удаление контактов пользователя: {email}')
                delete_contacts(email)
            else:
                break