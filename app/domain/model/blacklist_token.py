import datetime

from sqlalchemy import Column, String, Integer, DateTime

from .base import Base


class BlacklistToken(Base):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    token: str = Column(String(500), unique=True, nullable=False)
    blacklisted_on: datetime.datetime = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

