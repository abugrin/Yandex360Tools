#from time import time
import httpx
import requests
from typing import Self

class Resource():
    def __init__(self,
                 public_key: str,
                 public_url: str,
                 name: str,
                 created: str,
                 modified: str,
                 path: str,
                 type: str,
                 mime_type: str,
                 size: int,
                 ):
        self.__public_key: str = public_key
        self.__public_url: str = public_url
        self.__name: str = name
        self.__created: str = created
        self.__modified: str = modified
        self.__path: str = path
        self.__type: str = type
        self.__mime_type: str = mime_type
        self.__size: int = size

    @classmethod
    def from_dict(cls, obj: dict):
        try:
            return cls(
                public_key=obj['public_key'],
                public_url=obj['public_url'],
                name=obj.get('name', ''),
                created=obj['created'],
                modified=obj['modified'],
                path=obj['path'],
                type=obj['type'],
                mime_type=obj.get('mime_type', ''),
                size=obj.get('size', 0),
            )
        except KeyError as e:
            raise e
    
    @property
    def public_key(self) -> str:
        return self.__public_key
    @property
    def public_url(self) -> str:
        return self.__public_url
    @property
    def name(self) -> str:
        return self.__name
    @property
    def created(self) -> str:
        return self.__created
    @property
    def modified(self) -> str:
        return self.__modified
    @property
    def path(self) -> str:
        return self.__path
    @property
    def type(self) -> str:
        return self.__type
    @property
    def mime_type(self) -> str:
        return self.__mime_type
    @property
    def size(self) -> int:
        return self.__size

class PublicResourcesList():
    def __init__(self, items: list[Resource], type, limit, offset):
        self.__items: list[Resource] = items
        self.__type: str = type
        self.__limit: int = limit
        self.__offset: int = offset


    def join(self, resources: Self) -> Self:
        return PublicResourcesList(
            items=self.__items + resources.items,
            type=self.__type,
            limit=self.__limit,
            offset=self.__offset,
        )

    @classmethod
    def from_dict(cls, obj: dict):

        return cls(
            items=[Resource.from_dict(item) for item in obj['items']],
            type=obj.get('type', ''),
            limit=obj['limit'],
            offset=obj['offset'],
        )
    
    @property
    def items(self) -> list[Resource]:
        return self.__items
    @property
    def type(self) -> str:
        return self.__type
    @property
    def limit(self) -> int:
        return self.__limit
    @property
    def offset(self) -> int:
        return self.__offset
    

class PublicAccess():
    def __init__(self,
                 access_type: str,
                 macros: list[str],
                 rights: list[str],
                 org_id: str,
                 user_id: str
                 ):
        self.__access_type: str = access_type
        self.__macros: list[str] = macros
        self.__rights: list[str] = rights
        self.__org_id: str = org_id
        self.__user_id: str = user_id


    @classmethod
    def from_dict(cls, obj: dict):
        user_id = obj.get('id')
        if user_id:
            user_id = str(user_id)
        
        return cls(
            access_type=obj.get('type'),
            macros=obj.get('macros', []),
            rights=obj.get('rights', []),
            org_id=obj.get('org_id'),
            user_id=user_id
        )
    
    @property
    def access_type(self) -> str:
        return self.__access_type
    @property
    def macros(self) -> list[str]:
        return self.__macros[0]
    @property
    def rights(self) -> list[str]:
        return self.__rights[0]
    @property
    def org_id(self) -> str:
        return self.__org_id
    @property
    def user_id(self) -> str:
        return self.__user_id

    
class PublicSettings():
    def __init__(self, available_until, public_accesses: list[PublicAccess]):
        self.__available_until: str = available_until
        self.__public_accesses: list[PublicAccess] = public_accesses

    
    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            available_until=obj['available_until'],
            public_accesses=[PublicAccess.from_dict(access) for access in obj['accesses']],
        )

    @property
    def available_until(self) -> str:
        return self.__available_until
    
    @property
    def public_accesses(self) -> list[PublicAccess]:
        return self.__public_accesses


class DiskClientException(Exception):
    def __init__(self, message: str):
        self.message = message


class DiskClient():
    def __init__(self):
        self.__httpx_client = httpx.Client(base_url='https://cloud-api.yandex.net')


    def get_public_resources(self, token: str, limit: int = 100, offset: int = 0, type: str = None) -> PublicResourcesList:

        url = 'https://cloud-api.yandex.net/v1/disk/resources/public'
        headers = {'Authorization': 'OAuth ' + token}
        params = {
            'limit': limit,
            'offset': offset,
            'fields': 'limit,offset,items.public_key,items.public_url,items.name, items.created,items.modified,items.path,items.type,items.mime_type,items.size'
            }
        
        if type:
            params['type'] = type

        public_resource_list = PublicResourcesList(items=[], type='', limit=limit, offset=offset)
        
        while True:
            #start_time = time()
            res = self.__httpx_client.get(url, headers=headers, params=params)
            #end_time = time()
            #print(f'get_public_resources: {end_time - start_time}')
            self.__check_response(res)
            public_resource_part = PublicResourcesList.from_dict(res.json())
            if len(public_resource_part.items) == 0:
                break
            if len(public_resource_list.items) == 0:
                public_resource_list = public_resource_part
            else:
                public_resource_list = public_resource_list.join(public_resource_part)
            params['offset'] += limit
        return public_resource_list
        
    

    def get_public_settings(self, token: str, path: str) -> PublicSettings:
        url = '/v1/disk/public/resources/public-settings'
        headers = {'Authorization': 'OAuth ' + token}
        params = {'path': path, 'allow_address_access': True}
        #start_time = time()
        res = self.__httpx_client.get(url, headers=headers, params=params)
        #end_time = time()
        #print(f'get_public_settings: {end_time - start_time}')
        self.__check_response(res)
        
        public_settings = PublicSettings.from_dict(res.json())

        return public_settings    
    
    def __check_response(self, response: requests.Response):
        if response.status_code == 401:
            error_message = 'Error getting public resource. Please check if user is not blocked in your organization. '
            error_message += f'Response code: {response.status_code} Response message: {response.text}'

            raise DiskClientException(error_message)
                
        elif response.status_code != 200:
            raise Exception(f'Error getting public resource: {response.status_code} : {response.text}')

    def close(self):
        self.__httpx_client.close()
