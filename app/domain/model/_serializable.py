import datetime
from typing import Optional, List

from sqlalchemy import Column, DateTime


class Serializable:
    created_at: datetime.datetime = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    deleted_at: Optional[datetime.datetime] = Column(DateTime, index=True)
    _json_black_list: List[str] = []

    def validate(self):
        # add validation here
        pass

    def to_json(self, except_fields: str=[]) -> dict:
        json_data = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key not in self._json_black_list and key not in except_fields:
                if isinstance(value, (datetime.datetime, datetime.date)):
                    json_data[key] = value.isoformat()
                elif isinstance(value, list):
                    # fixme: without _json_black_list this code can make recursive reference. It
                    #  should have a better way to avoid the recursion
                    json_data[key] = [v.to_json() if hasattr(v, 'to_json') else v for v in value]
                else:
                    json_data[key] = value.to_json() if hasattr(value, 'to_json') else value
        return json_data

    def to_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    def __repr__(self):
        attrs = ", ".join([f"{attr}={repr(getattr(self, attr))}" for attr in self.to_dict()])
        return f"{self.__class__.__name__}({attrs})"
