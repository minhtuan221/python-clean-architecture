import datetime
from typing import Optional

from sqlalchemy import Column, DateTime


class Serializable:
    created_at: datetime.datetime = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    deleted_at: Optional[datetime.datetime] = Column(DateTime, index=True)

    def validate(self):
        # add validation here
        pass

    def to_json(self) -> dict:
        json_data = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, (datetime.datetime, datetime.date)):
                    json_data[key] = value.isoformat()
                else:
                    json_data[key] = value
        return json_data

    def to_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    def __repr__(self):
        attrs = ", ".join([f"{attr}={repr(getattr(self, attr))}" for attr in self.to_dict()])
        return f"{self.__class__.__name__}({attrs})"
