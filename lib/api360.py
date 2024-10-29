import asyncio
import logging
import sys

import aiohttp

from lib.types import User, UsersPage


class API360:
    __url = 'https://api360.yandex.net/directory/v1/org/'
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
                        raise Exception(f"Request failed with status {response.status}")
            else:
                if body:
                    async with session.post(url=path, headers=headers, body=body) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            raise Exception(f"Request failed with status {response.status}")
                elif data:
                    async with session.post(url=path, headers=headers, data=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            raise Exception(f"Request failed with status {response.status}")

    def get_user(self, user_id) -> User:
        path = f'{self.__url}{self._org_id}/users/{user_id}'
        response_json = asyncio.run(self._send_request(path, self._headers))
        return User.from_dict(response_json)


    async def count_pages(self)-> (int, int):
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
        path = f'{self.__url}{self._org_id}/users??page={page}&perPage={self.__per_page}'
        response_json = await self._send_request(path, self._headers)
        return UsersPage.from_dict(response_json)

    async def get_service_app_token(self, client_id, client_secret, subject_token, subject_token_type = 'urn:yandex:params:oauth:token-type:uid'):
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
        try:
            response_json = await self._send_request(path, headers, method='post', data=data)
            return response_json
        except Exception as e:
            self._logger.error(f"Error while getting service app token: {e}")
            raise e
