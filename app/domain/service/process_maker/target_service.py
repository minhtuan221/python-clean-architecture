from typing import List, Optional

from app.domain.model import Target, State, Route
from app.domain.model.process_maker.target import TargetType
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.group import GroupRepository
from app.infrastructure.persistence.process_maker.target import TargetRepository


class TargetService(object):

    def __init__(self,
                 target_repo: TargetRepository,
                 group_repo: GroupRepository):
        self.target_repo = target_repo
        self.group_repo = group_repo

    def create(self, name: str, description: str = '', target_type: str = TargetType.group,
               group_id: int = 0) -> Target:
        new_target = Target(name=name, description=description, target_type=target_type,
                            group_id=group_id)
        new_target.validate()

        if group_id:
            group = self.group_repo.find_one(group_id)
            new_target.group_id = group.id

        exist_record = self.target_repo.find_by_name(new_target.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist('name already exist')
        return self.target_repo.create(new_target)

    def find_one(self, target_id: int) -> Target:
        validation.validate_id(target_id)
        target = self.target_repo.find_one(target_id)
        if not target:
            raise error_collection.RecordNotFound
        return target

    def find_one_by_name(self, name: str) -> Target:
        target = self.target_repo.find_by_name(name)
        if not target:
            raise error_collection.RecordNotFound
        return target

    def search(self, name: str, page: int = 1, page_size: int = 10) -> List[Target]:
        targets = self.target_repo.search(name, page, page_size)
        return targets

    def update(self, target_id: int, name: str = '', description: str = '',
               target_type: str = '', group_id: int = 0) -> Target:
        target = self.find_one(target_id)
        if name:
            exist_record = self.target_repo.find_by_name(name)
            if exist_record:
                raise error_collection.RecordAlreadyExist(
                    f'target name ({target.name}) already exist')
            target.name = name
        if description:
            target.description = description
        if group_id:
            group = self.group_repo.find_one(group_id)
            target.group_id = group.id
        if target_type:
            target.target_type = target_type
        target.validate()

        target = self.target_repo.update(target)
        return target

    def delete(self, target_id: int):
        target = self.target_repo.delete(target_id)
        return target
