from curses.ascii import US
from enum import Enum
import json
from typing import List


class _BaseObject(object):
    def to_json(self):
        return json.dumps(self)


class Name(_BaseObject):
    def __init__(self, first, last, middle):
        self.__first = first
        self.__last = last
        self.__middle = middle

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            first=obj['first'],
            last=obj['last'],
            middle=obj['middle']
        )

    @property
    def first(self):
        return self.__first

    @property
    def last(self):
        return self.__last

    @property
    def middle(self):
        return self.__middle


class Contact(_BaseObject):
    def __init__(
            self,
            ctype,
            value,
            main,
            alias,
            synthetic
    ):
        self.__type = ctype
        self.__value = value
        self.__main = main
        self.__alias = alias
        self.__synthetic = synthetic

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            ctype=obj['type'],
            value=obj['value'],
            main=obj['main'],
            alias=obj['alias'],
            synthetic=obj['synthetic']
        )

    @property
    def type(self):
        return self.__type

    @property
    def value(self):
        return self.__value

    @property
    def main(self):
        return self.__main

    @property
    def alias(self):
        return self.__alias

    @property
    def synthetic(self):
        return self.__synthetic

class ShortUser(_BaseObject):
    def __init__(self, uid, nickname, department_id, email, name, gender, position, avatar_id):
        self.__uid = uid
        self.__nickname = nickname
        self.__department_id = department_id
        self.__email = email
        self.__name = name
        self.__gender = gender
        self.__position = position
        self.__avatar_id = avatar_id
    
    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            uid=obj['id'],
            nickname=obj['nickname'],
            department_id=obj['departmentId'],
            email=obj['email'],
            name=Name.from_dict(obj['name']),
            gender=obj['gender'],
            position=obj['position'],
            avatar_id=obj['avatarId']
        )
    
    @property
    def uid(self) -> str:
        return self.__uid
       
    @property
    def nickname(self) -> str:
        return self.__nickname
    
    @property
    def department_id(self) -> str:
        return self.__department_id
    
    @property
    def email(self) -> str:
        return self.__email
    
    @property
    def name(self) -> Name:
        return self.__name
    
    @property
    def gender(self) -> str:
        return self.__gender
    
    @property
    def position(self) -> str:
        return self.__position
    
    @property
    def avatar_id(self) -> str:
        return self.__avatar_id
    

class User(ShortUser):
    def __init__(
            self,
            uid,
            email,
            nickname,
            department_id,
            name,
            is_enabled,
            gender,
            position,
            avatar_id,
            about,
            birthday,
            external_id,
            is_admin,
            is_robot,
            is_dismissed,
            timezone,
            language,
            created_at,
            updated_at,
            display_name,
            groups,
            contacts,
            aliases
    ):
        super().__init__(uid, nickname, department_id, email, name, gender, position, avatar_id)
        self.__is_enabled = is_enabled
        self.__about = about
        self.__birthday = birthday
        self.__external_id = external_id
        self.__is_admin = is_admin
        self.__is_robot = is_robot
        self.__is_dismissed = is_dismissed
        self.__timezone = timezone
        self.__language = language
        self.__created_at = created_at
        self.__updated_at = updated_at
        self.__display_name = display_name
        self.__groups = groups
        self.__contacts = contacts
        self.__aliases = aliases

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            uid=obj['id'],
            email=obj['email'],
            nickname=obj['nickname'],
            department_id=obj['departmentId'],
            name=Name.from_dict(obj['name']),
            is_enabled=obj['isEnabled'],
            gender=obj['gender'],
            position=obj['position'],
            avatar_id=obj['avatarId'],
            about=obj['about'],
            birthday=obj['birthday'],
            external_id=obj['externalId'],
            is_admin=obj['isAdmin'],
            is_robot=obj['isRobot'],
            is_dismissed=obj['isDismissed'],
            timezone=obj['timezone'],
            language=obj['language'],
            created_at=obj['createdAt'],
            updated_at=obj['updatedAt'],
            display_name=obj.get('displayName', ''),
            groups=[group for group in obj.get('groups')],
            contacts=[Contact.from_dict(contact) for contact in obj['contacts']],
            aliases=[alias for alias in obj['aliases']]
        )

    @property
    def is_enabled(self):
        return self.__is_enabled

    @property
    def about(self):
        return self.__about

    @property
    def birthday(self):
        return self.__birthday

    @property
    def external_id(self):
        return self.__external_id

    @property
    def is_admin(self):
        return self.__is_admin

    @property
    def is_robot(self):
        return self.__is_robot

    @property
    def is_dismissed(self):
        return self.__is_dismissed

    @property
    def timezone(self):
        return self.__timezone

    @property
    def language(self):
        return self.__language

    @property
    def created_at(self):
        return self.__created_at

    @property
    def updated_at(self):
        return self.__updated_at

    @property
    def display_name(self):
        return self.__display_name

    @property
    def groups(self):
        return self.__groups

    @property
    def contacts(self):
        return self.__contacts

    @property
    def aliases(self):
        return self.__aliases


class UsersPage(_BaseObject):
    def __init__(self, users, page, pages, per_page, total):
        self._users = users
        self._page = page
        self._pages = pages
        self._per_page = per_page
        self._total = total

    @classmethod
    def from_dict(cls, obj):
        return cls(
            users=[User.from_dict(user) for user in obj['users']],
            page=obj['page'],
            pages=obj['pages'],
            per_page=obj['perPage'],
            total=obj['total'],
        )

    @property
    def users(self) -> List[User]:
        return self._users

    @property
    def pages(self):
        return self._pages

    @property
    def page(self):
        return self._page

    @property
    def per_page(self):
        return self._per_page

    @property
    def total(self):
        return self._total


class ShortGroup(_BaseObject):
    def __init__(self, group_id: int, group_name: str, members_count: int):
        self.__group_id = group_id
        self.__name = group_name
        self.__members_count = members_count

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            group_id=obj['id'],
            group_name=obj['name'],
            members_count=obj['membersCount']
        )

    @property
    def group_id(self) -> str:
        return self.__group_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def members_count(self) -> int:
        return self.__members_count

class GroupMemberType(Enum):
    USER = 'user'
    GROUP = 'group'
    DEPARTMENT = 'department'

class GroupMember(_BaseObject):
    def __init__ (self, member_id: str, type: GroupMemberType):
        self.__member_id = member_id
        self.__type = type

    @property
    def member_id(self) -> str:
        return self.__member_id

    @property
    def type(self) -> GroupMemberType:
        return self.__type
    
    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            member_id=obj['id'],
            type=GroupMemberType(obj['type'])
        )
    
class Group(ShortGroup):
    def __init__(
        self, 
        group_id: int,
        name: str,
        type: str,
        description: str,
        members_count: int,
        label: str,
        email: str,
        aliases: list[str],
        external_id: str,
        removed: bool,
        members: list[GroupMember],
        admin_ids: list[str],
        author_id: str,
        member_of: list[int],
        created_at: str
    ):
        super().__init__(group_id, name, members_count)
        self.__type = type
        self.__description = description
        self.__label = label
        self.__email = email
        self.__aliases = aliases
        self.__external_id = external_id
        self.__removed = removed
        self.__members = members
        self.__admin_ids = admin_ids
        self.__author_id = author_id
        self.__member_of = member_of
        self.__created_at = created_at

    @property
    def type(self) -> str:
        return self.__type
    
    @property
    def description(self) -> str:
        return self.__description

    @property
    def label(self) -> str:
        return self.__label

    @property
    def email(self) -> str:
        return self.__email

    @property
    def aliases(self) -> list[str]:
        return self.__aliases

    @property
    def external_id(self) -> str:
        return self.__external_id

    @property
    def removed(self) -> bool:
        return self.__removed

    @property
    def members(self) -> list[GroupMember]:
        return self.__members

    @property
    def admin_ids(self) -> list[str]:
        return self.__admin_ids

    @property
    def author_id(self) -> str:
        return self.__author_id

    @property
    def member_of(self) -> list[int]:
        return self.__member_of

    @property
    def created_at(self) -> str:
        return self.__created_at
    

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            group_id=obj['id'],
            name=obj['name'],
            type=obj['type'],
            description=obj['description'],
            members_count=obj['membersCount'],
            label=obj['label'],
            email=obj['email'],
            aliases=[alias for alias in obj['aliases']],
            external_id=obj['externalId'],
            removed=obj['removed'],
            members=[GroupMember.from_dict(member) for member in obj['members']],
            admin_ids=[admin_id for admin_id in obj['adminIds']],
            author_id=obj['authorId'],
            member_of=[m_of for m_of in obj['memberOf']],
            created_at=obj['createdAt']
        )
    
class GroupsPage(_BaseObject):
    def __init__(self, groups: list[Group], page: int, pages: int, per_page: int, total: int):
        self.__groups = groups
        self.__page = page
        self.__pages = pages
        self.__per_page = per_page
        self.__total = total

    @property
    def groups(self) -> list[Group]:
        return self.__groups

    @property
    def page(self) -> int:
        return self.__page

    @property
    def pages(self) -> int:
        return self.__pages

    @property
    def per_page(self) -> int:
        return self.__per_page

    @property
    def total(self) -> int:
        return self.__total

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            groups=[Group.from_dict(group) for group in obj['groups']],
            page=obj['page'],
            pages=obj['pages'],
            per_page=obj['perPage'],
            total=obj['total']
        )

class GroupMembers2(_BaseObject):
    def __init__(self, groups, users):
        self.__groups = groups
        self.__users = users

    @property
    def groups(self) -> list[ShortGroup]:
        return self.__groups
    
    @property
    def users(self) -> list[ShortUser]:
        return self.__users


    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            groups=[ShortGroup.from_dict(group) for group in obj['groups']],
            users=[ShortUser.from_dict(user) for user in obj['users']]
        )

