import asyncio
import logging
import sys
from time import sleep

import aiohttp
import requests

from lib.types import GroupMemberType, GroupMembers2, GroupsPage, User, UsersPage


class API360:
    __url = 'https://api360.yandex.net/directory/v1/org/'
    __url_v2 = 'https://api360.yandex.net/directory/v2/org/'
    __fetch_rate = 0.1
    __per_page = 100

    def __init__(self, api_key: str, org_id: str, log_level=logging.INFO):
        self._api_key = api_key
        self._org_id = org_id
        self._logger = logging.getLogger('api360')
        self._logger.setLevel(log_level)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
        self._logger.addHandler(log_handler)

        self._headers = {
            "Authorization": f"OAuth {api_key}",
            "content-type": "application/json",
        }
    '''
    def _send_request(self, path) -> Response:
        response = get(path, headers=self._headers)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Request failed with status {response.status_code}")
    '''
    @staticmethod
    async def _send_request(path, headers, method='get', body = None, data = None) -> dict:
        async with aiohttp.ClientSession() as session:
            if method == 'get':
                async with session.get(url=path, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Request failed with status {response.status} - {response} - {response.content}")
            else:
                if body:
                    async with session.post(url=path, headers=headers, json=body) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            raise Exception(f"Request failed with status {response.status} - {response}")
                elif data:
                    async with session.post(url=path, headers=headers, data=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            raise Exception(f"Request failed with status {response.status} - {response}")

    def get_user(self, user_id) -> User:
        path = f'{self.__url}{self._org_id}/users/{user_id}'
        response_json = asyncio.run(self._send_request(path, self._headers))
        return User.from_dict(response_json)


    async def count_pages(self)-> tuple[int, int]:
        """Get number of pages in users list response"""

        self._logger.debug(f"Counting users pages for organization: {self._org_id}")
        path = f'{self.__url}{self._org_id}/users?perPage={self.__per_page}'

        # response_json = asyncio.run(self._send_request(path, self._headers))
        response_json = await self._send_request(path, self._headers)
        self._logger.debug(f"Users response: {response_json}")
        pages_count = response_json['pages']
        users_count = response_json['total']
        return users_count, pages_count

    async def get_users_page(self, page) -> UsersPage:
        path = f'{self.__url}{self._org_id}/users?page={page}&perPage={self.__per_page}'
        response_json = await self._send_request(path, self._headers)
        return UsersPage.from_dict(response_json)
    
    def get_all_users(self) -> list[User]:
        """Get all users of an organization.

        Returns:
            list[User]: List of users
        """

        users = []
        _, total_pages = asyncio.run(self.count_pages())
        for page in range(1, total_pages + 1):
            users_page = asyncio.run(self.get_users_page(page))
            users.extend(users_page.users)
            sleep(self.__fetch_rate)
        return users
    
    def add_user_to_group(self, user_id: str, group_id: int) -> dict:
        """Add user to group. Use API v1 method: dev/api360/doc/ru/ref/GroupService/GroupService_AddMember

        Args:
            user_id (str): User ID
            group_id (int): Group ID

        Returns:
            dict: Response
        """

        path = f'{self.__url}{self._org_id}/groups/{group_id}/members'
        body = {
            "id": user_id,
            "type": GroupMemberType.USER.value
        }

        response_json = asyncio.run(self._send_request(path, self._headers, method='post', body=body))
        return response_json

    def get_groups(self, page: int = 1, per_page: int = 10) -> GroupsPage:
        """Get groups of an organization. Use API v1 method: https://yandex.ru/dev/api360/doc/ru/ref/GroupService/GroupService_List

        Args:
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Number of groups per page. Defaults to 10.

        Returns:
            GroupsPage: List of groups
        """

        path = f'{self.__url}{self._org_id}/groups?page={page}&perPage={per_page}'
        response_json = asyncio.run(self._send_request(path, self._headers))
        return GroupsPage.from_dict(response_json)
    

    def get_group_members_v2(self, group_id) -> GroupMembers2:
        """Get members of a group. Use API v2 method: https://yandex.ru/dev/api360/doc/ru/ref/GroupV2Service/GroupService_ListMembers

        Args:
            group_id (number): Group ID number. Use get_groups(page, per_page) to get IDs

        Returns:
            GroupMembers2: Object with lists of group members
        """

        path = f'{self.__url_v2}{self._org_id}/groups/{group_id}/members'
        response_json = asyncio.run(self._send_request(path, self._headers))

        return GroupMembers2.from_dict(response_json)

    async def get_service_app_token_async(client_id, client_secret, subject_token, subject_token_type = 'urn:yandex:params:oauth:token-type:uid'):
        path, headers, data = API360._get_headers(client_id, client_secret, subject_token, subject_token_type)
        response_json = await API360._send_request(path, headers, method='post', data=data)
        return response_json


    @staticmethod    
    def get_service_app_token(client_id, client_secret, subject_token, subject_token_type = 'urn:yandex:params:oauth:token-type:uid'):
        path, headers, data = API360._get_headers(client_id, client_secret, subject_token, subject_token_type)
        response_json = requests.post(path, headers=headers, data=data).json()
        return response_json

    @staticmethod
    def _get_headers(client_id, client_secret, subject_token, subject_token_type):
        path = 'https://oauth.yandex.ru/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'client_id': client_id,
            'client_secret': client_secret,
            'subject_token': subject_token,
            'subject_token_type': subject_token_type
        }

        return path, headers, data
