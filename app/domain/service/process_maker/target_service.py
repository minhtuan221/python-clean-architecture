from typing import List, Optional

from app.domain.model import Target, State, Route
from app.domain.model.process_maker.target import TargetType
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.process_maker.target import TargetRepository


class TargetService(object):

    def __init__(self,
                 target_repo: TargetRepository):
        self.target_repo = target_repo

    def create(self, name: str, description: str = '', action_type: str = TargetType.group) -> Target:
        new_action = Target(name=name, description=description, action_type=action_type)
        new_action.validate()

        exist_record = self.target_repo.find_by_name(new_action.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist('name already exist')
        return self.target_repo.create(new_action)

    def find_one(self, action_id: int, with_children: bool=True) -> Target:
        validation.validate_id(action_id)
        if with_children:
            action = self.target_repo.get_children_by_id(action_id)
        else:
            action = self.target_repo.find_one(action_id)
        if not action:
            raise error_collection.RecordNotFound
        return action

    def search(self, name: str, page: int = 1, page_size: int = 10) -> List[Target]:
        actions = self.target_repo.search(name, page, page_size)
        return actions

    def update(self, action_id: int, name: str = '', description: str = '',
               action_type: str = '') -> Target:
        action = self.find_one(action_id)
        if name:
            exist_record = self.target_repo.find_by_name(name)
            if exist_record:
                raise error_collection.RecordAlreadyExist(
                    f'action name ({action.name}) already exist')
            action.name = name
        if description:
            action.description = description
        if action_type:
            action.action_type = action_type
        action.validate()

        action = self.target_repo.update(action)
        return action

    def delete(self, action_id: int):
        action = self.target_repo.delete(action_id)
        return action


