from typing import List, Optional

from app.domain.model import Group
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.group import GroupRepository


class GroupService(object):

    def __init__(self, group_repo: GroupRepository):
        self.group_repo = group_repo

    def create(self, name: str, description: str = '') -> Group:
        new_group = Group(name=name, description=description)
        new_group.validate()

        exist_record = self.group_repo.find_by_name(new_group.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist('name already exists')
        return self.group_repo.create(new_group)

    def find_one(self, group_id: int) -> Group:
        validation.validate_id(group_id)
        group = self.group_repo.find_one(group_id)
        if not group:
            raise error_collection.RecordNotFound
        return group

    def find_one_by_name(self, name: str) -> Group:
        group = self.group_repo.find_by_name(name)
        if not group:
            raise error_collection.RecordNotFound
        return group

    def search(self, name: str, page: int = 1, page_size: int = 10) -> List[Group]:
        groups = self.group_repo.search(name, page, page_size)
        return groups

    def update(self, group_id: int, name: str = '', description: str = '') -> Group:
        group = self.find_one(group_id)
        if name:
            exist_record = self.group_repo.find_by_name(name)
            if exist_record:
                raise error_collection.RecordAlreadyExist(f'Group name ({group.name}) already exists')
            group.name = name
        if description:
            group.description = description
        group.validate()

        group = self.group_repo.update(group)
        return group

    def delete(self, group_id: int):
        group = self.group_repo.delete(group_id)
        return group
