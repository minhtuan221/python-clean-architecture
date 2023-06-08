from typing import List

from app.domain.model import Process
from app.domain.utils import error_collection, validation
from app.infrastructure.persistence.process import ProcessRepository


class ProcessService(object):

    def __init__(self, process_repo: ProcessRepository):
        self.process_repo = process_repo

    def create(self, name: str, description: str = '') -> Process:
        print('create ', name, description)
        new_process = Process(name=name, description=description)
        new_process.validate()

        exist_record = self.process_repo.find_by_name(new_process.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist('name already exist')
        return self.process_repo.create(new_process)

    def find_one(self, process_id: int) -> Process:
        validation.validate_id(process_id)
        process = self.process_repo.find_one(process_id)
        if not process:
            raise error_collection.RecordNotFound
        return process

    def search(self, name: str, page: int = 1, page_size: int = 10) -> List[Process]:
        processes = self.process_repo.search(name, page, page_size)
        return processes

    def update(self, process_id: int, name: str, description: str) -> Process:
        process = self.process_repo.find_one(process_id)
        process.name = name
        process.description = description
        process.validate()

        exist_record = self.process_repo.find_by_name(process.name)
        if exist_record:
            raise error_collection.RecordAlreadyExist('name already exist')

        process = self.process_repo.update(process)
        return process

    def delete(self, process_id: int):
        process = self.process_repo.delete(process_id)
        return process
