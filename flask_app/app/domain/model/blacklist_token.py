from datetime import datetime, timedelta
from typing import Optional
from collections import namedtuple
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from .base import Base

class BlacklistToken(Base):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    token: str = Column(String(500), unique=True, nullable=False)
    blacklisted_on: datetime = Column(DateTime, nullable=False)
    user_id: int = Column(Integer, nullable=False)

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
