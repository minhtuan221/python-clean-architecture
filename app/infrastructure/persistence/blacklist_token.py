from app.domain.model import ConnectionPool
from app.domain.model.user import User, Role
from app.domain.model import PermissionPolicy
from app.domain.model.blacklist_token import BlacklistToken
from app.pkgs import errors
from datetime import datetime
from typing import List


class BlacklistTokenRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def is_blacklist(self, auth_token):
        # check whether auth token has been blacklisted
        with self.db.new_session() as db:
            res = db.session.query(BlacklistToken).filter_by(
                token=str(auth_token)).first()
            if res:
                return True
            else:
                return False

    def add_token(self, auth_token):
        # check whether auth token has been blacklisted
        with self.db.new_session() as db:
            bl_token = BlacklistToken(token=str(auth_token))
            bl_token.blacklisted_on = datetime.utcnow()
            db.session.add(bl_token)
        return bl_token