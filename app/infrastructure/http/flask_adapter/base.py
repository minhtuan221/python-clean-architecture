from functools import wraps
from flask import jsonify
from app.pkgs.errors import Error, HttpStatusCode


class JsonResponse(object):
    def __init__(self, d=None, http_status: int = 200):
        if d is None:
            d = {}
        self.data: dict = d
        self.http_status = http_status

    def to_json(self):
        return self.data

    def code(self):
        return self.http_status


def json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            if type(e) is Error:
                return jsonify(e.to_json()), e.code()
            return jsonify(data=None, error=f'Unknown error: {str(e)}'), HttpStatusCode.Internal_Server_Error
        if isinstance(res, JsonResponse):
            return jsonify(res.to_json()), res.code()
        if res is not None:
            return jsonify(data=res)
        return jsonify(data=[])
    return wrapper
