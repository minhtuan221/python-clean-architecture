from app.domain.model import ConnectionPool, AccessPolicy, Role, User
from datetime import datetime
from sqlalchemy import or_


class AccessPolicyRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def change_user(self, user: User, note: object = 'change in user') -> object:
        with self.db.new_session() as db:
            checker = AccessPolicy(user_id=user.id, note=note)
            checker.denied_before = datetime.utcnow()
            db.session.add(checker)
        return checker

    def change_role(self, role: Role, note: str = 'change in role'):
        with self.db.new_session() as db:
            checker = AccessPolicy(role_id=role.id, note=note)
            checker.denied_before = datetime.utcnow()
            db.session.add(checker)
        return checker

    def find_for_token_validation(self, user_id, role_ids):
        with self.db.new_session() as db:
            checker: AccessPolicy = db.session.query(AccessPolicy) \
                .filter(or_(AccessPolicy.user_id == user_id, AccessPolicy.role_id.in_(role_ids))) \
                .order_by(AccessPolicy.denied_before.desc()) \
                .first()
        return checker
