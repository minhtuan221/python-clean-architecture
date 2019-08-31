import re
from cerberus import Validator
from app.pkgs.type_check import type_check
from app.domain.model import errors


@type_check
def validate_id(id: int):
    if id > 0:
        return None
    return errors.Error('Missing ID or ID must greater than 0')

@type_check
def validate_name(name: str):
    print('name', name)
    print(re.match("^[a-zA-Z0-9_.-]+$", 'admin') is None)
    if re.match("^[a-zA-Z0-9_.-]+$", name) is None:
        return errors.Error('It should contain a-z, A-Z, 0-9, _, -, . without any space')
    return None


@type_check
def validate_email(email: str):
    if re.match(r"^((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)$", email) is None:
        return errors.Error('Email validation failed')
    return None

@type_check
def validate_password(passwd: str): 
      
    special_symbol =['$', '@', '#', '%'] 
      
    if len(passwd) < 6: 
        return errors.Error('length should be at least 6') 
          
    if len(passwd) > 20: 
        return errors.Error('length should be not be greater than 20') 
          
    if not any(char.isdigit() for char in passwd): 
        return errors.Error('Password should have at least one numeral') 
          
    if not any(char.isupper() for char in passwd): 
        return errors.Error('Password should have at least one uppercase letter') 
          
    if not any(char.islower() for char in passwd): 
        return errors.Error('Password should have at least one lowercase letter') 
          
    if not any(char in special_symbol for char in passwd): 
        return errors.Error(f'Password should have at least one of the symbols {special_symbol}') 
    
    return None

