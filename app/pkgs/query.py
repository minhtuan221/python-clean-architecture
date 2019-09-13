from .type_check import type_check


@type_check
def get_start_stop_pos(page: int, size: int):
    page = max(1, page)
    size = max(1, size)
    offset = (page - 1) * size
    limit = size
    return offset, limit
