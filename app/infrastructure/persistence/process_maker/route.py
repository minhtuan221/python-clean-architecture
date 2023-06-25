from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import Route
from app.domain.utils.db_helper import get_limit_offset


class RouteRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, route: Route) -> Route:
        with self.db.new_session() as db:
            route.created_at = datetime.now()
            route.updated_at = datetime.now()
            db.session.add(route)
        return route

    def find_one(self, route_id: int) -> Optional[Route]:
        with self.db.new_session() as db:
            route: Route = db.session.query(Route).filter_by(
                id=route_id).first()
        return route

    def find_by_parent(self, process_id: int, route_id: int) -> Optional[Route]:
        with self.db.new_session() as db:
            route: Route = db.session.query(Route)\
                .filter(Route.id==route_id)\
                .filter(Route.process_id==process_id)\
                .first()
        return route

    def find_for_duplication(self, process_id: int, current_state_id: int, next_state_id: int) -> Optional[Route]:
        with self.db.new_session() as db:
            route: Route = db.session.query(Route) \
                .filter(Route.current_state_id == current_state_id) \
                .filter(Route.next_state_id == next_state_id) \
                .filter(Route.process_id == process_id) \
                .first()
        return route

    def search(self, page: int = 1, page_size: int = 20) -> List[Route]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            routes: List[Route] = db.session.query(Route).offset(offset).limit(limit).all()
        return routes

    def update(self, route: Route) -> Route:
        with self.db.new_session() as db:
            route.updated_at = datetime.now()
            db.session.add(route)
        return route

    def delete(self, route_id: int) -> Optional[Route]:
        with self.db.new_session() as db:
            route: Route = self.find_one(route_id)
            if not route:
                return route
            route.process_id = None
            route.deleted_at = datetime.now()
            db.session.add(route)
        return route
