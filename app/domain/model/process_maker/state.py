import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.model.process_maker.state_type import StateType
from app.domain.utils import validation, error_collection


class State(Base, Serializable):
    __tablename__ = 'state'
    id: int = Column(Integer, primary_key=True)
    process_id: int = Column(Integer, ForeignKey('process.id'))
    name: str = Column(String(128))
    description: str = Column(String(500))
    state_type: str = Column(String(128))

    process = relationship("Process", back_populates="state")
    route = relationship("Route", back_populates="current_state")
    activity = relationship("Activity", secondary='state_activity', back_populates="state")

    _json_black_list = ['process']

    def validate(self):
        return
        self.name = self.name.strip()
        self.description = self.description.strip()
        # more validate here
        validation.validate_name(self.name)
        validation.validate_short_paragraph(self.description)
        self.state_type = self.state_type.strip().lower()
        if self.state_type not in StateType.__dict__.values():
            raise error_collection.ValidationError(f'invalid state_type, receive {self.state_type}')


class StateActivity(Base, Serializable):
    __tablename__ = 'state_activity'
    state_id: int = Column(Integer, ForeignKey('state.id'), primary_key=True)
    activity_id: int = Column(Integer, ForeignKey('activity.id'), primary_key=True)
