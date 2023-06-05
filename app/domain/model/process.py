import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime

from app.domain.model import Base
from app.domain.model._serializable import Serializable


class Process(Base, Serializable):
    __tablename__ = 'processes'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))

