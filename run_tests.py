from app.infrastructure.factory_bot.setup_test import setup_before_tests
from tests.domain.service.test_process_maker import TestProcessMakerService
from tests.domain.service.test_user import TestUserService
from tests.domain.service.test_user_role import TestUserRoleService
from tests.infrastructure.http.test_process_api import TestProcessAPI
from tests.pkgs.test_injector import TestContainer

test_cases = [
    setup_before_tests,
    TestContainer,
    TestUserRoleService,
    TestUserService,
    TestProcessAPI,
    TestProcessMakerService
]
