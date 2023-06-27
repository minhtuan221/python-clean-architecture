from typing import List, Optional

from app.domain.model import Process, State, Route
from app.domain.model.process_maker.process import ProcessStatus
from app.domain.model.process_maker.state_type import StateType
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.process_maker.action import ActionRepository
from app.infrastructure.persistence.process_maker.activity import ActivityRepository
from app.infrastructure.persistence.process_maker.process import ProcessRepository
from app.infrastructure.persistence.process_maker.request import RequestRepository
from app.infrastructure.persistence.process_maker.route import RouteRepository
from app.infrastructure.persistence.process_maker.state import StateRepository


class ProcessService(object):

    def __init__(self,
                 process_repo: ProcessRepository,
                 action_repo: ActionRepository,
                 activity_repo: ActivityRepository,
                 route_repo: RouteRepository,
                 state_repo: StateRepository,
                 request_repo: RequestRepository):
        self.process_repo = process_repo
        self.action_repo = action_repo
        self.activity_repo = activity_repo
        self.route_repo = route_repo
        self.state_repo = state_repo
        self.request_repo = request_repo

    def create(self, name: str, description: str = '') -> Process:
        new_process = Process(name=name, description=description)
        new_process.status = ProcessStatus.inactive
        new_process.validate()

        exist_record = self.process_repo.find_by_name(new_process.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist(f'name ({name}) already exist')
        return self.process_repo.create(new_process)

    def find_one(self, process_id: int, with_children: bool = False) -> Process:
        validation.validate_id(process_id)
        if with_children:
            process = self.process_repo.get_children_by_process_id(process_id)
        else:
            process = self.process_repo.find_one(process_id)
        if not process:
            raise error_collection.RecordNotFound(f"process ({process_id}) not found")
        return process

    def find_one_by_name(self, name: str) -> Process:
        process = self.process_repo.find_by_name(name)
        if not process:
            raise error_collection.RecordNotFound
        return process

    def search(self, name: str, page: int = 1, page_size: int = 10) -> List[Process]:
        processes = self.process_repo.search(name, page, page_size)
        return processes

    def update(self, process_id: int, name: str = '', description: str = '',
               status: str = '') -> Process:
        process = self.find_one(process_id)
        if name:
            exist_record = self.process_repo.find_by_name(name)
            if exist_record:
                raise error_collection.RecordAlreadyExist(
                    f'process name ({process.name}) already exist')
            process.name = name
        if description:
            process.description = description
        if status:
            process.status = status
        process.validate()

        process = self.process_repo.update(process)
        return process

    def delete(self, process_id: int):
        process = self.process_repo.delete(process_id)
        return process

    # state service
    def add_state_to_process(self, process_id: int, name: str, description: str = '',
                             state_type: str = 'start') -> State:
        process = self.find_one(process_id)
        state = State(name=name, description=description, state_type=state_type)
        state.validate()
        # check duplicate name
        self.check_duplicate_state(process_id, name)
        state.process = process
        return self.state_repo.create(state)

    def find_state_on_process(self, process_id: int, state_id: int) -> State:
        state = self.state_repo.find_by_parent(process_id, state_id)
        if not state:
            raise error_collection.RecordNotFound(f'cannot find state_id ({state_id})')
        return state

    def find_state_on_process_by_name(self, process_id: int, name: str) -> State:
        state = self.state_repo.find_by_name_and_parent(process_id, name)
        if not state:
            raise error_collection.RecordNotFound(f'cannot find state name ({name})')
        return state

    def find_start_point(self, process_id: int) -> State:
        return self.find_state_by_type(process_id, state_type=StateType.start)

    def find_state_by_type(self, process_id: int, state_type: str) -> State:
        list_state = self.state_repo.search(process_id=process_id, page_size=2000)
        for state in list_state:
            if state.state_type == state_type:
                return state
        raise error_collection.RecordNotFound(f'cannot find state with type=({state_type})')

    def check_duplicate_state(self, process_id: int, name: str):
        dup_state = self.state_repo.find_by_name_and_parent(process_id, name)
        if dup_state:
            raise error_collection.ValidationError(f'duplicate name state, receive {name}')

    def update_state_on_process(self, process_id: int, state_id: int, name: str = '',
                                description: str = '',
                                state_type: str = ''):
        state = self.find_state_on_process(process_id, state_id)
        name = name.strip()
        if name and name != state.name:
            # check duplicate name
            self.check_duplicate_state(process_id, name)
            state.name = name
        if description:
            state.description = description
        if state_type:
            state.state_type = state_type
        state.validate()
        return self.state_repo.update(state)

    def remove_state_from_process(self, process_id: int, state_id: int) -> State:
        state = self.find_state_on_process(process_id, state_id)
        return self.state_repo.delete(state.id)

    def add_activity_to_state(self, process_id: int, state_id: int, activity_id: int) -> State:
        activity = self.activity_repo.find_one(activity_id)
        state = self.find_state_on_process(process_id, state_id)
        state.activity.append(activity)
        self.state_repo.update(state)
        return state

    def remove_activity_from_state(self, process_id: int, state_id: int, activity_id: int) -> State:
        activity = self.activity_repo.find_one(activity_id)
        state = self.find_state_on_process(process_id, state_id)
        state.activity.remove(activity)
        self.state_repo.update(state)
        return state

    # route service
    def add_route_to_process(self, process_id: int, current_state_id: int,
                             next_state_id: int = 0) -> Route:
        process = self.find_one(process_id)
        current_state = self.find_state_on_process(process_id, current_state_id)
        # find duplicate route, allow one route from state to state only
        self.check_duplicate_route(process.id, current_state_id, next_state_id)
        route = Route(process_id=process_id)
        route.current_state = current_state
        route.current_state_id = current_state.id
        if next_state_id:
            next_state = self.find_state_on_process(process_id, next_state_id)
            route.next_state_id = next_state.id
        route.validate()
        return self.route_repo.create(route)

    def check_duplicate_route(self, process_id: int, current_state_id: int, next_state_id: int):
        dup_route = self.route_repo.find_for_duplication(process_id, current_state_id, next_state_id)
        if dup_route:
            raise error_collection.RecordAlreadyExist('the route between 2 states already exist')

    def find_route_on_process(self, process_id: int, route_id: int) -> Route:
        route = self.route_repo.find_by_parent(process_id, route_id)
        if not route:
            raise error_collection.RecordNotFound(f'cannot find route_id ({route_id})')
        return route

    def update_route_on_process(self, process_id: int, route_id: int, current_state_id: int = 0,
                                next_state_id: int = -1):
        route = self.find_route_on_process(process_id, route_id)
        if current_state_id:
            route.current_state_id = current_state_id
        if next_state_id >= -1:
            route.next_state_id = next_state_id
        route.validate()
        # find duplicate route, allow one route from state to state only
        self.check_duplicate_route(process_id, current_state_id, next_state_id)
        return self.route_repo.update(route)

    def remove_route_from_process(self, process_id: int, route_id: int) -> State:
        route = self.find_route_on_process(process_id, route_id)

        self.route_repo.delete(route.id)
        return route

    def add_activity_to_route(self, process_id: int, route_id: int, activity_id: int) -> State:
        activity = self.activity_repo.find_one(activity_id)
        route = self.find_route_on_process(process_id, route_id)
        route.activity.append(activity)
        self.route_repo.update(route)
        return route

    def remove_activity_from_route(self, process_id: int, route_id: int, activity_id: int) -> State:
        activity = self.activity_repo.find_one(activity_id)
        route = self.find_route_on_process(process_id, route_id)
        route.activity.remove(activity)
        self.route_repo.update(route)
        return route

    def add_action_to_route(self, process_id: int, route_id: int, action_id: int) -> State:
        action = self.action_repo.find_one(action_id)
        route = self.find_route_on_process(process_id, route_id)
        route.action.append(action)
        self.route_repo.update(route)
        return route

    def remove_action_from_route(self, process_id: int, route_id: int, action_id: int) -> State:
        action = self.action_repo.find_one(action_id)
        route = self.find_route_on_process(process_id, route_id)
        route.action.remove(action)
        self.route_repo.update(route)
        return route
