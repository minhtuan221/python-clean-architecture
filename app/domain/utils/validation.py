import re

from app.pkgs import errors
from app.pkgs.type_check import type_check

special_symbol = ['$', '@', '#', '%']


@type_check
def validate_id(_id: int) -> int:
    if _id is None:
        raise ValueError(f'ID should not be {_id}')
    if _id > 0:
        return _id
    raise errors.Error('Missing ID or ID must greater than 0')


@type_check
def validate_name_without_space(name: str) -> str:
    if len(name) > 128:
        raise errors.Error('Name should not be longer than 128 characters')
    if re.match("^[a-zA-Z0-9_.-]+$", name) is None:
        raise errors.Error(f'It should contain a-z, A-Z, 0-9, _, -, . without any space, receive {name}')
    return name


def validate_name(name: str) -> str:
    if len(name) > 128:
        raise errors.Error('Name should not be longer than 128 characters')
    if re.match("^[a-zA-Z0-9_. -]+$", name) is None:
        raise errors.Error(
            f'It should contain a-z, A-Z, 0-9, _, -, ., and spaces without any leading/trailing spaces, receive {name}')
    return name


@type_check
def validate_short_paragraph(paragraph: str) -> str:
    if len(paragraph) > 500:
        raise errors.Error('Paragraph should not be longer than 500 characters')
    return paragraph.strip()


@type_check
def validate_medium_paragraph(paragraph: str) -> str:
    if len(paragraph) > 4000:
        raise errors.Error('Paragraph should not be longer than 4000 characters')
    return paragraph.strip()


@type_check
def validate_email(email: str) -> str:
    if len(email) > 128:
        raise errors.Error('email should not be longer than 128 characters')
    if re.match(
            r"^((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)$",
            email) is None:
        raise errors.Error('Email validation type failed')
    return email


@type_check
def validate_password(passwd: str) -> str:
    if len(passwd) < 6:
        raise errors.Error('length should be at least 6')

    if len(passwd) > 20:
        raise errors.Error('length should be not be greater than 20')

    if not any(char.isdigit() for char in passwd):
        raise errors.Error('Password should have at least one numeral')

    if not any(char.isupper() for char in passwd):
        raise errors.Error('Password should have at least one uppercase letter')

    if not any(char.islower() for char in passwd):
        raise errors.Error('Password should have at least one lowercase letter')

    if not any(char in special_symbol for char in passwd):
        raise errors.Error(f'Password should have at least one of the symbols {special_symbol}')

    return passwd
