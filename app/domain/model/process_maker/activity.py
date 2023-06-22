import datetime
from dataclasses import asdict
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.model.process_maker.activity_type import ActivityType
from app.domain.utils import validation, error_collection


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

    def validate(self):
        return
        self.name = self.name.strip()
        validation.validate_name(self.name)
        self.description = self.description.strip()
        validation.validate_short_paragraph(self.description)
        self.activity_type = self.activity_type.strip().lower()
        if self.activity_type not in ActivityType.__dict__.values():
            raise error_collection.ValidationError(f'invalid activity_type, receive {self.activity_type}')


class ActivityTarget(Base, Serializable):
    __tablename__ = 'activity_target'
    activity_id: int = Column(Integer, ForeignKey('activity.id'), primary_key=True)
    target_id: int = Column(Integer, ForeignKey('target.id'), primary_key=True)

