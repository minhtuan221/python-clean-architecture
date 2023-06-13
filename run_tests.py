from app.infrastructure.factory_bot.setup_test import setup_before_tests
from tests.domain.service.test_process_maker import TestProcessMakerService
from tests.domain.service.test_user import TestUserService
from tests.domain.service.test_user_role import TestUserRoleService
from tests.infrastructure.http.test_action_api import TestActionAPI
from tests.infrastructure.http.test_activity_api import TestActivityAPI
from tests.infrastructure.http.test_group_api import TestGroupAPI
from tests.infrastructure.http.test_process_api import TestProcessAPI
from tests.infrastructure.http.test_target_api import TestTargetAPI
from tests.pkgs.test_injector import TestContainer

test_cases = [
    setup_before_tests,
    TestContainer,
    TestUserRoleService,
    TestUserService,
    TestActionAPI,
    TestProcessAPI,
    TestActivityAPI,
    TestGroupAPI,
    TestTargetAPI,
    TestProcessMakerService
]
