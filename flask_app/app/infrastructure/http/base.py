from functools import wraps
from flask import jsonify

class JsonResponse(object):
    def __init__(self, d: dict, error: Exception = None, http_status: int = 200):
        self.data: dict = d
        self.data['error'] = str(error)
        self.http_status = http_status
    
    def to_json(self):
        return self.data, self.http_status

def json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res: JsonResponse = func(*args, **kwargs)
        if isinstance(res, JsonResponse):
            return jsonify(res.to_json()), res.http_status
        return jsonify(res)
    return wrapper

