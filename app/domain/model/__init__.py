from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as db_session
from typing import Callable
from sqlalchemy.orm import scoped_session

Base = declarative_base()

# It's must to list all model here
from app.domain.model.user import User, UserRole
from app.domain.model.role import Role, PermissionPolicy
from app.domain.model.blacklist_token import BlacklistToken
from app.domain.model.access_policy import AccessPolicy


class ConnectionPool(object):
    def __init__(self, connection_string: str, echo=False):
        self.engine = create_engine(connection_string, echo=echo)
        self.connection_string: str = connection_string
        session_factory = scoped_session(sessionmaker(
            bind=self.engine, expire_on_commit=False))
        self.session_factory = session_factory

    def new_session(self):
        new_session = self.session_factory()
        return SQLAlchemyDBConnection(self.connection_string,
                                      engine=self.engine,
                                      session=new_session)


class SQLAlchemyDBConnection(object):
    """SQLAlchemy database connection"""

    def __init__(self, connection_string: str, engine=None, session=None):
        if engine:
            self.engine = engine
        else:
            self.engine = create_engine(connection_string)
        self.connection_string: str = connection_string
        self.session: db_session = session
        self.error = None

    def __enter__(self):
        # session_factory = sessionmaker(bind=self.engine)
        # Session = scoped_session(session_factory)
        # self.session = Session()
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


@contextmanager
def session_scope(self, handler: Callable = None) -> db_session:
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

