
import csv
import logging
import os


from lib.types import User

from dotenv import load_dotenv
from lib.api360 import API360


load_dotenv()

FETCH_RATE = 0.1

api = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.INFO)


def get_user_by_email(email: str, org_users) -> User:
    return next((user for user in org_users if user.email == email), None)

def read_users_to_groups_csv(file_path: str) -> list[dict]:
    users_to_groups = []
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_email = row.get('Email')
                group_id = row.get('GroupId')
                if user_email and group_id and group_id.isdigit():
                    users_to_groups.append(row)
                    
        return users_to_groups
    except FileNotFoundError:
        print(f'Файл {file_path} не найден')
        exit(1)


def main():
    org_users = api.get_all_users()
    print(f'- Загружено пользователей организации: {len(org_users)}')

    users_to_groups = read_users_to_groups_csv('users_to_groups.csv')
    print(f'- Загружено пользователей из CSV: {len(users_to_groups)}')

    for user_to_group in users_to_groups:
        user_email = user_to_group.get('Email')
        group_id = user_to_group.get('GroupId')

        user = get_user_by_email(user_email, org_users)
        if user:
            try:
                res = api.add_user_to_group(user.uid, int(group_id))
                if res.get('added'):
                    print(f'-- {user_email} добавлен в группу {group_id}')
                else:
                    print(f'-- {user_email} НЕ добавлен в группу {group_id}')
            except Exception as e:
                print(f'-- {user_email} ОШИБКА при добавлении пользователя в группу {group_id}: {e}')


if __name__ == '__main__':
    print('- Старт импорта пользователей в группы')
    main()
    print('- Завершен импорт пользователей в группы')


    exit(0)
