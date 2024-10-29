import json
from typing import List


class _BaseObject(object):
    def to_json(self):
        return json.dumps(self)


class Name(_BaseObject):
    def __init__(self, first, last, middle):
        self._first = first
        self._last = last
        self._middle = middle

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            first=obj['first'],
            last=obj['last'],
            middle=obj['middle']
        )

    @property
    def first(self):
        return self._first

    @property
    def last(self):
        return self._last

    @property
    def middle(self):
        return self._middle


class Contact(_BaseObject):
    def __init__(
            self,
            ctype,
            value,
            main,
            alias,
            synthetic
    ):
        self._type = ctype
        self._value = value
        self._main = main
        self._alias = alias
        self._synthetic = synthetic

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
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def main(self):
        return self._main

    @property
    def alias(self):
        return self._alias

    @property
    def synthetic(self):
        return self._synthetic


class User(_BaseObject):
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
        self._uid = uid
        self._email = email
        self._nickname = nickname
        self._department_id = department_id
        self._name = name
        self._is_enabled = is_enabled
        self._gender = gender
        self._position = position
        self._avatar_id = avatar_id
        self._about = about
        self._birthday = birthday
        self._external_id = external_id
        self._is_admin = is_admin
        self._is_robot = is_robot
        self._is_dismissed = is_dismissed
        self._timezone = timezone
        self._language = language
        self._created_at = created_at
        self._updated_at = updated_at
        self._display_name = display_name
        self._groups = groups
        self._contacts = contacts
        self._aliases = aliases

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
    def uid(self) -> str:
        return self._uid

    @property
    def email(self) -> str:
        return self._email

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def department_id(self) -> str:
        return self._department_id

    @property
    def name(self):
        return self._name

    @property
    def is_enabled(self):
        return self._is_enabled

    @property
    def gender(self):
        return self._gender

    @property
    def position(self):
        return self._position

    @property
    def avatar_id(self):
        return self._avatar_id

    @property
    def about(self):
        return self._about

    @property
    def birthday(self):
        return self._birthday

    @property
    def external_id(self):
        return self._external_id

    @property
    def is_admin(self):
        return self._is_admin

    @property
    def is_robot(self):
        return self._is_robot

    @property
    def is_dismissed(self):
        return self._is_dismissed

    @property
    def timezone(self):
        return self._timezone

    @property
    def language(self):
        return self._language

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def display_name(self):
        return self._display_name

    @property
    def groups(self):
        return self._groups

    @property
    def contacts(self):
        return self._contacts

    @property
    def aliases(self):
        return self._aliases


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
