from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Group(Base, Serializable):
    __tablename__ = 'group'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))

    member = relationship("User", secondary='group_member', back_populates="group")

    def validate(self):
        self.name = self.name.strip()
        self.description = self.description.strip()
        # more validate here
        validation.validate_name(self.name)
        validation.validate_short_paragraph(self.description)

class GroupMember(Base):
    __tablename__ = 'group_member'
    user_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id: int = Column(Integer, ForeignKey('group.id'), primary_key=True)


