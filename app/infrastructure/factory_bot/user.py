from app.cmd.center_store import container
from app.domain.model import User
from app.domain.service.user import UserService


def gen_or_get_normal_user(email, password) -> User:
    user_service = container.get_singleton(UserService)
    if not user_service.is_exist_email(email):
        user = user_service.create_new_user(email, password)
    else:
        user = user_service.find_by_email(email)
    return user


def gen_token_for_normal_user(email='test_bot@gmail.com', password='1Pass@word') -> str:
    user_service = container.get_singleton(UserService)
    gen_or_get_normal_user(email, password)
    return user_service.login(email, password)