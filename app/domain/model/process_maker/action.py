import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Action(Base, Serializable):
    """Actions: Things a user can perform on a Request."""
    __tablename__ = 'action'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))
    action_type: str = Column(String(128))

    route = relationship("Route", secondary='route_action', back_populates="action")
    target = relationship("Target", secondary='action_target', back_populates="action")


class ActionTarget(Base, Serializable):
    __tablename__ = 'action_target'
    action_id: int = Column(Integer, ForeignKey('action.id'), primary_key=True)
    target_id: int = Column(Integer, ForeignKey('target.id'), primary_key=True)

