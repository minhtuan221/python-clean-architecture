import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Target(Base, Serializable):
    """The Targets table does us no good unless we can relate it to other tables that can
    actually use the Targets. We want to use Targets in two scenarios:

    As people who can perform Actions
    As people who can receive Activities"""
    __tablename__ = 'target'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))
    target_type: str = Column(String(128), default='group')   # default is group but can be other entity in future
    group_id: int = Column(Integer)
    """When using a Group as a Target, the way the system interprets this relationship is different.

    If the Group is an Action Target, then any member of the Group can perform the action for it to be valid.
    If the Group is an Activity Target, then all members of the Group receive the Activity (e.g. everyone in the group gets an email)."""

    action = relationship("Action", secondary='action_target', back_populates="target")
    activity = relationship("Activity", secondary='activity_target', back_populates="target")
