import asyncio
import csv
import logging
import os
from time import sleep
from dotenv import load_dotenv
from lib.api360 import API360


load_dotenv()

FETCH_RATE = 0.1

api = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.INFO)


def fetch_all_users(pages):
    """Fetch all users per page."""
    org_users = []
    for page in range(1, pages + 1):
        org_users.extend(fetch_users_by_page(page))
        sleep(FETCH_RATE)
    print(f"Всего загружено пользователей: {len(org_users)}")
    return org_users


def fetch_users_by_page(page):
    """Fetch all users from exact page"""

    print(f"Загрузка пользователей. Страница {page}")
    org_users = []
    users_page = asyncio.run(api.get_users_page(page))
    for org_user in users_page.users:
        org_users.append(
            {
                'ID': org_user.uid,
                'Email': org_user.email,
                'Login': org_user.nickname,
                'Fname': org_user.name.first,
                'Lname': org_user.name.last,
                'Mname': org_user.name.middle,
                'DisplayName': org_user.display_name,
                'Position': org_user.position,
                'Language': org_user.language,
                'Timezone': org_user.timezone,
                'Admin': org_user.is_admin,
                'Enabled': org_user.is_enabled
            })

    return org_users


def save_users_to_csv(user_records):
    with open('users.csv', 'w', newline='', encoding='utf-8') as f:
        keys = user_records[0].keys()
        # noinspection PyTypeChecker
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(user_records)


if __name__ == '__main__':
    total_users, total_pages = asyncio.run(api.count_pages())
    print(f"Всего пользователей: {total_users}")
    print(f"Всего страниц: {total_pages}")

    start = input("Пользователи будут импортированы в файл users.csv. Начинаем? y/n: ")
    if start.lower() == 'y':
        users = fetch_all_users(total_pages)
        save_users_to_csv(users)
        print('Готово!')

    exit(0)
