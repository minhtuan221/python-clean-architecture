from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.model.process_maker.action_type import ActionType
from app.domain.utils import validation, error_collection


class Action(Base, Serializable):
    """Actions: Things a user can perform on a Request."""
    __tablename__ = 'action'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))
    action_type: str = Column(String(128))

    route = relationship("Route", secondary='route_action', back_populates="action")
    target = relationship("Target", secondary='action_target', back_populates="action")
    request_action = relationship("RequestAction", back_populates="action")

    _json_black_list = ['route']

    def validate(self):
        return
        self.name = self.name.strip()
        validation.validate_name(self.name)
        self.description = self.description.strip()
        validation.validate_short_paragraph(self.description)
        self.action_type = self.action_type.strip().lower()
        if self.action_type not in ActionType.__dict__.values():
            raise error_collection.ValidationError(f'invalid action type, receive {self.action_type}')

    def get_route(self) -> 'Route':
        return self.route


class ActionTarget(Base, Serializable):
    __tablename__ = 'action_target'
    action_id: int = Column(Integer, ForeignKey('action.id'), primary_key=True)
    target_id: int = Column(Integer, ForeignKey('target.id'), primary_key=True)


