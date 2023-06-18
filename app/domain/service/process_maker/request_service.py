import json
import pprint
from typing import List

from app.domain.model import Request, RequestData, RequestNote, RequestStakeholder, User, Action, \
    Route
from app.domain.model.process_maker.request import DataType, NoteType, RequestAction
from app.domain.service.group_service import GroupService
from app.domain.service.process_maker.action_service import ActionService
from app.domain.service.process_maker.activity_service import ActivityService
from app.domain.service.process_maker.process_service import ProcessService
from app.domain.service.user import UserService
from app.domain.utils import error_collection
from app.infrastructure.persistence.process_maker.request import RequestRepository
from app.infrastructure.persistence.process_maker.request_action import RequestActionRepository
from app.infrastructure.persistence.process_maker.request_data import RequestDataRepository
from app.infrastructure.persistence.process_maker.request_note import RequestNoteRepository
from app.infrastructure.persistence.process_maker.request_stakeholder import \
    RequestStakeholderRepository


class RequestService(object):

    def __init__(self,
                 request_repo: RequestRepository,
                 request_note_repo: RequestNoteRepository,
                 request_action_repo: RequestActionRepository,
                 request_data_repo: RequestDataRepository,
                 request_stakeholder_repo: RequestStakeholderRepository,
                 user_service: UserService,
                 group_service: GroupService,
                 process_service: ProcessService,
                 action_service: ActionService,
                 activity_service: ActivityService):
        self.request_repo = request_repo
        self.request_note_repo = request_note_repo
        self.request_action_repo = request_action_repo
        self.request_data_repo = request_data_repo
        self.request_stakeholder_repo = request_stakeholder_repo
        self.user_service = user_service
        self.group_service = group_service
        self.process_service = process_service
        self.action_service = action_service
        self.activity_service = activity_service

    def add_request_data(self, request: Request, value: dict, name: str='content', data_type: str = 'json') -> Request:
        request_data = RequestData(data_type=data_type, status='active', name=name)
        request_data.value = json.dumps(value) if data_type==DataType.json else value
        request_data.validate()
        request.request_data.append(request_data)
        return request

    def add_request_note(self, request: Request, note: str, user_id: int = 0, note_type=NoteType.user_note) -> Request:
        request_note = RequestNote(user_id=user_id, note=note, note_type=note_type)
        request_note.validate()
        request.request_note.append(request_note)
        return request

    def add_request_stakeholder(self, request: Request, stakeholder_id: int, stakeholder_type: str = 'user') -> Request:
        request_stakeholder = RequestStakeholder(stakeholder_id=stakeholder_id, stakeholder_type=stakeholder_type)
        request_stakeholder.validate()
        request.request_stakeholder.append(request_stakeholder)
        return request

    def add_request_action(self, user_id: int, request: Request, action: Action, route: Route):
        request_action = RequestAction(user_id=user_id)
        request
        request_action.action_id = action.id
        request_action.route_id = route.id

    def create_request(
        self,
        process_id: int,
        user_id: int,
        title: str,
        content: dict,
        note: str,
        stakeholders: List[int],
        entity_model: str = '',
        entity_id: int = 0,
    ) -> Request:
        # Check if the process exists
        process = self.process_service.find_one(process_id)
        # Check if user_id exists
        user = self.user_service.find_by_id(user_id)

        # Check if user has the right to open the request in the process workflow (edit request action)
        # Create a new request
        request = Request(title=title, entity_id=entity_id, entity_model=entity_model)
        request.process = process
        request.user = user

        # Add request data
        request = self.add_request_data(request, value=content, name=entity_model)

        # Add request note
        request = self.add_request_note(request, note, user_id=user_id)

        # Add request stakeholder
        for stakeholder_id in stakeholders:
            request = self.add_request_stakeholder(request, stakeholder_id)

        # add state to request
        state = self.process_service.find_start_point(request.process_id)
        request.current_state = state
        return self.request_repo.create(request)

    def find_one_request(self, request_id: int, user_id: int=0):
        # todo: should have another method which receive user_id and check if user_id in
        #  request_stakeholder or in action_target
        request = self.request_repo.find_one(request_id)
        if not request:
            raise error_collection.RecordNotFound
        return request

    def find_request_allowed_action(self, request_id: int, user_id: int):
        request = self.find_one_request(request_id, user_id)
        routes = request.get_route()
        actions = []
        for route in routes:
            actions.extend(route.action)
        for i in range(len(actions)):
            actions[i] = self.action_service.find_one(actions[i].id)
        return actions

    def should_user_commit_action(self, user_id: int, action: Action) -> bool:
        group_ids = [group.id for group in action.target]
        for group_id in group_ids:
            if self.group_service.is_user_in_group(group_id, user_id):
                return True
        return False

    def find_request_allowed_action_for_specific_user(self, request_id: int, user_id: int, specific_user_id: int):
        actions = self.find_request_allowed_action(request_id, user_id)
        specific_user = self.user_service.find_by_id(specific_user_id)
        return [action for action in actions if self.should_user_commit_action(specific_user.id, action)]

    def user_commit_action(self, request_id: int, user_id: int, action_id: int):
        # find the action
        action = self.action_service.find_one(action_id)
        # check if user can commit this action
        allowed_action = self.find_request_allowed_action_for_specific_user(request_id, user_id=0, specific_user_id=user_id)
        if action.id not in [a.id for a in allowed_action]:
            raise error_collection.DontHaveRight(f"user ({user_id}) do not have right to commit this action")
        # get the route of the action
        route = action.get_route()
        # add request action

        # check if the route trigger change state of request

        return

    def find_request_actions(self, request_id: int, user_id: int=0):
        request = self.find_one_request(request_id, user_id)
        return [request_action for request_action in request.request_action]

