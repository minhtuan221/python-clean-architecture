import pytest

from app.cmd.center_store import container
from app.domain.model import ConnectionPool
from app.pkgs.atomic_counter import AtomicInteger


@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    # Code to run before tests start
    print("Setup before tests")
    # You can perform any necessary setup or initialization here
    connection_pool = container.get_singleton(ConnectionPool)
    connection_pool.open_test_session()

    yield  # Tests will be executed

    # Code to run after all tests finish

    connection_pool.close_test_session()
    print("Teardown after tests")
    # You can perform any necessary teardown or cleanup here


counter = AtomicInteger(0)
