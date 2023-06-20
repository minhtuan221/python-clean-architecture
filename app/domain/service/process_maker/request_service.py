import json
import pprint
from typing import List

from app.domain.model import Request, RequestData, RequestNote, RequestStakeholder, User, Action, \
    Route, Activity
from app.domain.model.process_maker.activity_type import ActivityType
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

    def _add_request_data(self, request: Request, value: dict, name: str= 'content', data_type: str = 'json') -> Request:
        request_data = RequestData(data_type=data_type, status='active', name=name)
        request_data.value = json.dumps(value) if data_type==DataType.json else value
        request_data.request_id = request.id
        request_data.validate()
        self.request_data_repo.create(request_data)
        return request

    def _add_request_note(self, request: Request, note: str, user_id: int = 0, note_type=NoteType.user_note) -> Request:
        request_note = RequestNote(user_id=user_id, note=note, note_type=note_type)
        request_note.request_id = request.id
        request_note.validate()
        self.request_note_repo.create(request_note)
        return request

    def _add_request_stakeholder(self, request: Request, stakeholder_id: int, stakeholder_type: str = 'user') -> Request:
        request_stakeholder = RequestStakeholder(stakeholder_id=stakeholder_id, stakeholder_type=stakeholder_type)
        request_stakeholder.request_id = request.id
        request_stakeholder.validate()
        self.request_stakeholder_repo.create(request_stakeholder)
        return request

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
        # check if start state is ok
        state = self.process_service.find_start_point(process.id)

        # Check if user has the right to open the request in the process workflow (edit request action)
        # Create a new request
        request = Request(title=title, entity_id=entity_id, entity_model=entity_model)
        request.process_id = process.id
        request.user_id = user.id
        request = self.request_repo.create(request)

        # Add request data
        self._add_request_data(request, value=content, name=entity_model)

        # Add request note
        self._add_request_note(request, note, user_id=user_id)

        # Add request stakeholder
        for stakeholder_id in stakeholders:
            self._add_request_stakeholder(request, stakeholder_id)

        # add state to request
        request.current_state_id = state.id
        return self.request_repo.update(request)

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

    def _should_user_commit_action(self, user_id: int, action: Action) -> bool:
        group_ids = [group.id for group in action.target]
        for group_id in group_ids:
            if self.group_service.is_user_in_group(group_id, user_id):
                return True
        return False

    def find_request_allowed_action_for_specific_user(self, request_id: int, user_id: int, specific_user_id: int):
        actions = self.find_request_allowed_action(request_id, user_id)
        specific_user = self.user_service.find_by_id(specific_user_id)
        return [action for action in actions if self._should_user_commit_action(specific_user.id, action)]

    def _add_request_action(self, request: Request, user: User, committed_action: Action):
        routes = request.get_route()
        turning_route = None
        actions = []
        for route in routes:
            for act in route.action:
                if act.id == committed_action.id:
                    actions.append(act)
                    turning_route = route

        # all actions, which user is allowed to commit
        allowed_actions = [action for action in actions if self._should_user_commit_action(user.id, action)]

        if not allowed_actions or not turning_route:
            raise error_collection.DontHaveRight(f"user ({user.id}) do not have right to commit this action")
        request_action = RequestAction(user_id=user.id)
        request_action.route_to_next_state = turning_route
        request_action.route_id = turning_route.id
        request_action.request_id = request.id
        request_action.action_id = committed_action.id
        request_action.validate()
        request.request_action.append(request_action)

        # trigger activity of route
        for act in turning_route.activity:
            self._trigger_activity(request, act, user, committed_action)
        return request_action

    def _trigger_activity(self, request: Request, activity: Activity, user: User, committed_action: Action):
        if activity.activity_type == ActivityType.add_note:
            self._add_request_note(request, note=committed_action.name, user_id=user.id, note_type=NoteType.system_note)
        elif activity.activity_type == ActivityType.send_email:
            # todo: add send email here
            for stakeholder in request.request_stakeholder:
                stakeholder_user = self.user_service.find_by_id(stakeholder.stakeholder_id)
                if stakeholder_user:
                    print(f'send email to {stakeholder_user.email_name()} (stakeholder) that {user.email_name()} {committed_action.name}')
        elif activity.activity_type == ActivityType.add_stakeholder:
            # todo: add action here
            print(f"activity do add stakeholder")
        elif activity.activity_type == ActivityType.remove_stakeholder:
            # todo: add action here
            print(f"activity do remove stakeholder")
        else:
            raise ValueError(f"receive unsupported activity={activity.name} type={activity.activity_type}")

    def _change_request_state(self, request: Request, request_action: RequestAction) -> bool:
        # this action is accepted => disable all other action
        for request_action in request.request_action:
            request_action.status = 'done'
        # trigger the change state of request id
        if request_action.route_to_next_state.next_state_id:
            # there are route that does not have next state id. it will not change state.
            # for example: edit action will not change the state
            request.current_state = self.process_service.find_state_on_process(request.process_id, request_action.route_to_next_state.next_state_id)
            return True
        return False

    def user_commit_action(self, request_id: int, user_id: int, action_id: int):
        request = self.find_one_request(request_id)
        user = self.user_service.find_by_id(user_id)
        # find the action
        action = self.action_service.find_one(action_id)
        # add request action
        request_action = self._add_request_action(request, user, action)
        is_changed = self._change_request_state(request, request_action)
        # trigger activity of new state
        if is_changed:
            for act in request.current_state.activity:
                self._trigger_activity(request, act, user, action)
        return self.request_repo.update(request)

    def find_request_actions(self, request_id: int, user_id: int=0):
        request = self.find_one_request(request_id, user_id)
        return [request_action for request_action in request.request_action]

