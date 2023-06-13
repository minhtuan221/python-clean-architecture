from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Process(Base, Serializable):
    __tablename__ = 'process'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))
    status: str = Column(String(64), default='inactive')  # default is active

    state = relationship("State", back_populates="process")
    route = relationship("Route", back_populates="process")
    request = relationship("Request", back_populates="process")

    _json_black_list = ['request']

    def validate(self):
        self.name = self.name.strip()
        self.description = self.description.strip()
        # more validate here
        validation.validate_name_with_space(self.name)
        validation.validate_short_paragraph(self.description)


class ProcessAdmin(Base):
    __tablename__ = 'process_admin'
    process_id: int = Column(Integer, ForeignKey('process.id'), primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
