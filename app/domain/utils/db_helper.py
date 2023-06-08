from app.pkgs.errors import Error


def get_limit_offset(page: int, page_size: int):
    if page < 1 or page_size < 1:
        raise Error("Page and page_size must be positive integers.")

    offset = (page - 1) * page_size
    limit = page_size

    return limit, offset

