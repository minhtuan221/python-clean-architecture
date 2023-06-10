import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Activity(Base, Serializable):
    """Activities: Things that result from a Request moving to a particular State or following a
    particular Transition. """
    __tablename__ = 'activity'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))
    activity_type: str = Column(String(128))

    route = relationship("Route", secondary='route_activity', back_populates="activity")
    state = relationship("State", secondary='state_activity', back_populates="activity")
    target = relationship("Target", secondary='activity_target', back_populates="activity")


class ActivityTarget(Base, Serializable):
    __tablename__ = 'activity_target'
    activity_id: int = Column(Integer, ForeignKey('activity.id'), primary_key=True)
    target_id: int = Column(Integer, ForeignKey('target.id'), primary_key=True)

