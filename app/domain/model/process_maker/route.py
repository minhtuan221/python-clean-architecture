import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Route(Base, Serializable):
    __tablename__ = 'route'
    id: int = Column(Integer, primary_key=True)
    process_id: int = Column(Integer, ForeignKey('process.id'))
    current_state_id: int = Column(Integer, ForeignKey('state.id'))
    next_state_id: int = Column(Integer)  # can be null or 0 if the action with it does not link to any state

    process = relationship("Process", back_populates="route")
    current_state = relationship("State", foreign_keys=[current_state_id], back_populates="route")
    action = relationship("Action", secondary='route_action', back_populates="route")
    activity = relationship("Activity", secondary='route_activity', back_populates="route")

    _json_black_list = ['process', 'current_state']


class RouteAction(Base, Serializable):
    __tablename__ = 'route_action'
    route_id: int = Column(Integer, ForeignKey('route.id'), primary_key=True)
    action_id: int = Column(Integer, ForeignKey('action.id'), primary_key=True)


class RouteActivity(Base, Serializable):
    __tablename__ = 'route_activity'
    route_id: int = Column(Integer, ForeignKey('route.id'), primary_key=True)
    activity_id: int = Column(Integer, ForeignKey('activity.id'), primary_key=True)

