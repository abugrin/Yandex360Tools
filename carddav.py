
import time
from dotenv import load_dotenv
import requests

from tools import get_service_app_token

load_dotenv()

def read_contacts(email: str):
    token = get_service_app_token(email)

    session = requests.Session()
    session.auth = (email, token)

    response = session.get(f'https://carddav.yandex.ru/addressbook/{email}/1/?op=ls')
    print(response.status_code)
    contacts_list = response.json().get('list')


    for contact in contacts_list:
        file_name = contact.get('fileName')
        print(f'File: {file_name} tag: {contact.get('etag')}')
        contact_data = response = session.get(f'https://carddav.yandex.ru/addressbook/{email}/1/{file_name}')
        print (contact_data.text)
        time.sleep(0.1)

def delete_contacts(email: str):
    token = get_service_app_token(email)

    session = requests.Session()
    session.auth = (email, token)

    response = session.get(f'https://carddav.yandex.ru/addressbook/{email}/1/?op=ls')
    print(response.status_code)

    contacts_list = response.json().get('list')

    for contact in contacts_list:
        file_name = contact.get('fileName')
        print(f'File: {file_name} tag: {contact.get('etag')}')
        response = session.delete(f'https://carddav.yandex.ru/addressbook/{email}/1/{file_name}')
        time.sleep(0.1)

if __name__ == '__main__':

    email = input('Введите email пользователя: ')
    
    print('1) Посмотреть список личных контактов')
    print('2) Удалить все личные контакты')
    print('3) Выход')

    choice = input('Выберите действие: ')

    if choice == '1':
        read_contacts(email)