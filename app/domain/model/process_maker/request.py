from typing import List

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base, Route
from app.domain.model._serializable import Serializable
from app.domain.utils import validation, error_collection


class DataType:
    json = 'json'
    text = 'text'


class NoteType:
    user_note = 'user_note'
    system_note = 'system_note'


class StakeholderType:
    user = 'user'
    group = 'group'


class RequestStatus:
    active = 'active'
    archived = 'archived'
    done = 'done'


class Request(Base, Serializable):
    """
    Entity model default is ''.
    - If it's a deal, entity_model'll be 'deal', entity_id'll be deal_id
    - if it's empty '', that mean no model and request data can be anything
    """
    __tablename__ = 'request'
    id: int = Column(Integer, primary_key=True)
    title: str = Column(String(500))
    user_id: int = Column(Integer, ForeignKey('users.id'))
    process_id: int = Column(Integer, ForeignKey('process.id'))
    current_state_id: int = Column(Integer, ForeignKey('state.id'))
    status: str = Column(String(64), default='active')  # default is active
    entity_model: str = Column(String(128), default='')
    entity_id: int = Column(Integer, default=0)

    process = relationship("Process", back_populates="request")
    current_state = relationship("State", foreign_keys=[current_state_id])
    user = relationship("User", back_populates="request")
    request_note = relationship("RequestNote", back_populates="request")
    request_data = relationship("RequestData", back_populates="request")
    request_action = relationship("RequestAction", back_populates="request")
    request_stakeholder = relationship("RequestStakeholder", back_populates="request")

    _json_black_list = ['process']

    def get_route(self) -> List[Route]:
        return self.current_state.route

    def validate(self):
        self.title = validation.validate_short_paragraph(self.title)
        if self.entity_model:
            self.entity_model = validation.validate_name_without_space(self.entity_model)
        if not self.status:
            self.status = RequestStatus.active
        self.status = self.status.strip()
        if self.status not in RequestStatus.__dict__.values():
            raise error_collection.ValidationError(f"invalid status, receive {self.status}")


class RequestNote(Base, Serializable):
    """RequestNote can be use as a note/comment or notify by system

    As note by user: user_id=1, 'I change the date in deal'
    As note by system: user_id=1, 'just update a new request data'
    """
    __tablename__ = 'request_note'
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer)  # will be the target of the note (who write it or it's caused by that user)
    request_id: int = Column(Integer, ForeignKey('request.id'))
    note_type: str = Column(String(64))  # default is user_note, can be system_note
    status: str = Column(String(64), default='active')  # default is active
    note: str = Column(String(4000))
    request = relationship("Request", back_populates="request_note")

    _json_black_list = ['request']

    def validate(self):
        self.note_type = self.note_type.strip().lower()
        if self.note_type not in NoteType.__dict__.values():
            raise error_collection.ValidationError(f"invalid note type, receive {self.note_type}")
        if not self.status:
            self.status = RequestStatus.active
        self.status = self.status.strip()
        if self.status not in RequestStatus.__dict__.values():
            raise error_collection.ValidationError(f"invalid status, receive {self.status}")
        self.note = validation.validate_medium_paragraph(self.note)


class RequestData(Base, Serializable):
    """RequestData is where we store the data attach to a request

    For example:

    - If deal_id=10, model='deal'. The request data will have name='deal', value=Deal(id=10).to_json(), data_type='deal'. The value must follow schema of the deal
    - If user change the deal => the request is updated also and the current request_data will be set
    state='archived'. The new deal data will be set to a new request data
    - If entity model in request is empty, the name will be 'content', the value will be any value user put in it without any schema

    """
    __tablename__ = 'request_data'
    id: int = Column(Integer, primary_key=True)
    request_id: int = Column(Integer, ForeignKey('request.id'))
    data_type: str = Column(String(64))  # 'json' or the model name of the request entity model
    status: str = Column(String(64), default='active')  # default is active
    name: str = Column(String(128))  # 'content' or the model of deal (eg: CertificateDeposit)
    value: str = Column(String(4000))  # string or the detail of the deal in json format
    request = relationship("Request", back_populates="request_data")

    _json_black_list = ['request']

    def validate(self):
        if not self.status:
            self.status = RequestStatus.active
        self.status = self.status.strip()
        if self.status not in RequestStatus.__dict__.values():
            raise error_collection.ValidationError(f"invalid status, receive {self.status}")
        if not self.name:
            self.name = 'content'
        self.name = validation.validate_name_without_space(self.name)
        self.value = validation.validate_medium_paragraph(self.value)
        if not self.data_type:
            self.data_type = DataType.text
        self.data_type = self.data_type.strip().lower()
        if self.data_type not in DataType.__dict__.values():
            raise error_collection.ValidationError(f"invalid data type, receive {self.data_type}")


class RequestStakeholder(Base, Serializable):
    """user when a group or a user is cc in a request"""
    __tablename__ = 'request_stakeholder'
    id: int = Column(Integer, primary_key=True)
    request_id: int = Column(Integer, ForeignKey('request.id'))
    stakeholder_id: int = Column(Integer)  # will be user_id or group_id
    stakeholder_type: str = Column(String(64), default='user')  # 'user' or group
    request = relationship("Request", back_populates="request_stakeholder")

    _json_black_list = ['request']

    def validate(self):
        if not self.stakeholder_type:
            self.stakeholder_type = StakeholderType.user
        if self.stakeholder_type not in StakeholderType.__dict__.values():
            raise error_collection.ValidationError(f"invalid stakeholder, receive {self.stakeholder_type}")
        if not self.stakeholder_id or self.stakeholder_id <= 0:
            raise error_collection.ValidationError(f"missing stakeholder id")

class RequestAction(Base, Serializable):
    """RequestAction is the real action of user which can route from state to state"""
    __tablename__ = 'request_action'
    id: int = Column(Integer, primary_key=True)
    request_id: int = Column(Integer, ForeignKey('request.id'))
    action_id: int = Column(Integer, ForeignKey('action.id'))
    user_id: int = Column(Integer, ForeignKey('users.id'))  # who made this action
    route_id: int = Column(Integer, ForeignKey('route.id'))
    status: str = Column(String(64), default='active')  # can be active|done|revert

    route_to_next_state: Route = None

    request = relationship("Request", back_populates="request_action")
    action = relationship("Action", back_populates="request_action")

    _json_black_list = ['request']

    def validate(self):
        if not self.status:
            self.status = RequestStatus.active
        self.status = self.status.strip()
        if self.status not in RequestStatus.__dict__.values():
            raise error_collection.ValidationError(f"invalid status, receive {self.status}")
