from dataclasses import dataclass

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation, error_collection


@dataclass
class TargetType:
    group = 'group'
    user = 'user'


class Target(Base, Serializable):
    """The Targets table does us no good unless we can relate it to other tables that can
    actually use the Targets. We want to use Targets in two scenarios:

    As people who can perform Actions
    As people who can receive Activities"""
    __tablename__ = 'target'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))
    target_type: str = Column(String(128), default=TargetType.group)   # default is group but can be user also
    group_id: int = Column(Integer)
    """When using a Group as a Target, the way the system interprets this relationship is different.

    If the Group is an Action Target, then any member of the Group can perform the action for it to be valid.
    If the Group is an Activity Target, then all members of the Group receive the Activity (e.g. everyone in the group gets an email)."""

    action = relationship("Action", secondary='action_target', back_populates="target")
    activity = relationship("Activity", secondary='activity_target', back_populates="target")

    def validate(self):
        self.name = self.name.strip()
        self.description = self.description.strip()
        # more validate here
        validation.validate_name(self.name)
        validation.validate_short_paragraph(self.description)
        self.target_type = self.target_type.strip().lower()
        if not self.target_type:
            self.target_type = TargetType.group
        if self.target_type not in TargetType.__dict__.values():
            raise error_collection.ValidationError(f'invalid target_type, receive {self.target_type}')
        self.group_id = int(self.group_id)
        if self.group_id <= 0:
            # group_id can be 0 it the action/activity have no target
            raise error_collection.ValidationError(f'invalid group id, receive {self.group_id}')

