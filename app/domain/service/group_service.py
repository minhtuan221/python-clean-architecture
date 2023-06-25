from typing import List, Optional

from app.domain.model import Group, GroupMember
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.group import GroupRepository
from app.infrastructure.persistence.user import UserRepository


class GroupService(object):

    def __init__(self, group_repo: GroupRepository, user_repo: UserRepository):
        self.group_repo = group_repo
        self.user_repo = user_repo

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
        validation.validate_id(group_id)
        group = self.group_repo.delete(group_id)
        return group

    def add_user_to_group(self, group_id: int, user_id: int) -> Group:
        group = self.group_repo.find_one(group_id)
        if not group:
            raise error_collection.RecordNotFound(f'cannot find group_id ({group_id})')

        user = self.user_repo.find(user_id)
        if not user:
            raise error_collection.RecordNotFound(f'cannot find user_id ({user_id})')

        group.member.append(user)

        # Update the group in the repository
        return self.group_repo.update(group)

    def remove_user_from_group(self, group_id: int, user_id: int) -> Group:
        group = self.group_repo.find_one(group_id)
        if not group:
            raise error_collection.RecordNotFound(f'cannot find group_id ({group_id})')

        user = self.user_repo.find(user_id)
        if not user:
            raise error_collection.RecordNotFound(f'cannot find user_id ({user_id})')

        group.member.remove(user)

        # Update the group in the repository
        return self.group_repo.update(group)

    def is_user_in_group(self,group_id: int, user_id: int) -> bool:
        group_member = self.group_repo.is_user_in_group(group_id, user_id)
        if group_member:
            return True
        return False
