from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Callable
from sqlalchemy.orm import scoped_session

Base = declarative_base()

# It must list all model here
from app.domain.model.user import User, UserRole
from app.domain.model.role import Role, PermissionPolicy
from app.domain.model.blacklist_token import BlacklistToken
from app.domain.model.access_policy import AccessPolicy
from app.domain.model.process import Process


class ConnectionPool(object):
    def __init__(self, connection_string: str, echo: bool = False):
        self.engine = create_engine(connection_string, echo=echo)
        self.connection_string: str = connection_string
        session_factory = scoped_session(
            sessionmaker(bind=self.engine, expire_on_commit=False, autocommit=False)
        )
        self.session_factory = session_factory
        self._test_session: Session = None
        self._is_test: bool = False
        self._test_engine = None

    def open_test_session(self):
        print('warning: this is test session. Do not use in production')
        # create_engine("sqlite:///:memory:") will work as well, but we use file to make more real
        # world tests
        self._test_engine = create_engine('sqlite:///./test_session.db', echo=False)
        self._test_session = scoped_session(
            sessionmaker(bind=self._test_engine, expire_on_commit=False, autocommit=False)
        )
        # should drop database first
        Base.metadata.drop_all(self._test_engine)
        # Create database tables
        Base.metadata.create_all(self._test_engine)
        self._is_test = True

    def close_test_session(self):
        self._test_session.close()
        self._test_session = None
        self._is_test = False
        print('\nwarning: test session is closed')

    def new_session(self):
        if self._is_test:
            return TestDBConnection(self._test_session)
        new_session = self.session_factory()
        return SQLAlchemyDBConnection(session=new_session)


class SQLAlchemyDBConnection(object):
    """SQLAlchemy database connection"""

    def __init__(self, session: Session):
        self.session: Session = session
        self.error = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.error = e
            raise e
        finally:
            self.session.close()
            self.error = None


class TestDBConnection(SQLAlchemyDBConnection):
    """SQLAlchemy database connection for test only"""

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.error = e
            raise e
        finally:
            # don't need to close test session
            pass


@contextmanager
def session_scope(self, handler: Callable = None) -> Session:
    """Provide a transactional scope around a series of operations.
    It can work with asyncIO and thread-safe
    """
    session_factory = sessionmaker(bind=self.engine)
    # create a Session
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        if handler:
            handler(e)
    finally:
        session.close()

    # def run_my_program():
    #     with session_scope() as session:
    #         ThingOne().go(session)
    #         ThingTwo().go(session)


def init_database(connection_string: str = "mysql://admin:123456@/field_sale"):
    engine = create_engine(connection_string, echo=True)

    def msg(msg, *args):
        msg = msg % args
        print("\n\n\n" + "-" * len(msg.split("\n")[0]))
        print(msg)
        print("-" * len(msg.split("\n")[0]))

    msg("Creating Tree Table:")

    Base.metadata.create_all(engine)
