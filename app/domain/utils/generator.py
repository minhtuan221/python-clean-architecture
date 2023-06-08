import random
import string
import time

from app.domain.utils.validation import special_symbol


def generate_email(prefix: str = 'test'):
    time.sleep(0.001)  # Add a delay of 1 millisecond
    timestamp = int(time.time() * 1000)
    return f"{prefix}{timestamp}@example.com"


def generate_name(prefix: str = 'test'):
    time.sleep(0.001)  # Add a delay of 1 millisecond
    timestamp = int(time.time() * 1000)
    return f"{prefix} {timestamp}"


def gen_reset_password():
    """generate 8 character password
    :return: string - password
    """
    uppercase = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
    lowercase = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
    digit = random.choice(string.digits)
    symbol = random.choice(special_symbol)
    password = lowercase + digit + symbol + uppercase
    return password


