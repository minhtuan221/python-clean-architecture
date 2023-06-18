from app.cmd.center_store import container
from app.domain.model import User
from app.domain.service.user import UserService
from app.pkgs.cache_tools import cache


def create_or_get_normal_user(email: str, password='1Pass@word') -> User:
    user_service = container.get_singleton(UserService)
    if not user_service.is_exist_email(email):
        user = user_service.create_new_user(email, password)
    else:
        user = user_service.find_by_email(email)
    user.token = user_service.login(email, password)
    return user


@cache
def get_token_for_normal_user(email='test_bot@test_mail.com', password='1Pass@word') -> str:
    user = create_or_get_normal_user(email, password)
    return user.token
