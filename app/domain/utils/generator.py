import time


def generate_email(prefix: str = 'test'):
    time.sleep(0.001)  # Add a delay of 1 millisecond
    timestamp = int(time.time() * 1000)
    return f"{prefix}{timestamp}@example.com"


def generate_name(prefix: str = 'test'):
    time.sleep(0.001)  # Add a delay of 1 millisecond
    timestamp = int(time.time() * 1000)
    return f"{prefix} {timestamp}"
