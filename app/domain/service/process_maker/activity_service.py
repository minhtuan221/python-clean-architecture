from typing import List, Optional

from app.domain.model import Activity, State, Route
from app.domain.model.process_maker.activity_type import ActivityType
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.process_maker.activity import ActivityRepository
from app.infrastructure.persistence.process_maker.target import TargetRepository


class ActivityService(object):

    def __init__(self,
                 activity_repo: ActivityRepository,
                 target_repo: TargetRepository):
        self.activity_repo = activity_repo
        self.target_repo = target_repo

    def create(self, name: str, description: str = '',
               activity_type: str = ActivityType.add_note) -> Activity:
        new_activity = Activity(name=name, description=description, activity_type=activity_type)
        new_activity.validate()

        exist_record = self.activity_repo.find_by_name(new_activity.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist('name already exist')
        return self.activity_repo.create(new_activity)

    def find_one(self, activity_id: int, with_children: bool = True) -> Activity:
        validation.validate_id(activity_id)
        if with_children:
            activity = self.activity_repo.get_children_by_id(activity_id)
        else:
            activity = self.activity_repo.find_one(activity_id)
        if not activity:
            raise error_collection.RecordNotFound
        return activity

    def search(self, name: str, page: int = 1, page_size: int = 10) -> List[Activity]:
        activities = self.activity_repo.search(name, page, page_size)
        return activities

    def update(self, activity_id: int, name: str = '', description: str = '',
               activity_type: str = '') -> Activity:
        activity = self.find_one(activity_id)
        if name:
            exist_record = self.activity_repo.find_by_name(name)
            if exist_record:
                raise error_collection.RecordAlreadyExist(
                    f'activity name ({activity.name}) already exist')
            activity.name = name
        if description:
            activity.description = description
        if activity_type:
            activity.activity_type = activity_type
        activity.validate()

        activity = self.activity_repo.update(activity)
        return activity

    def delete(self, activity_id: int):
        activity = self.activity_repo.delete(activity_id)
        return activity
