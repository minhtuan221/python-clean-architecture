import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime

from app.domain.model import Base
from app.domain.model._serializable import Serializable
from app.domain.utils import validation


class Process(Base, Serializable):
    __tablename__ = 'processes'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128))
    description: str = Column(String(500))

    def validate(self):
        self.name = self.name.strip()
        self.description = self.description.strip()
        # more validate here
        validation.validate_name_with_space(self.name)
        validation.validate_short_paragraph(self.description)

