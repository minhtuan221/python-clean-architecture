import requests
from fastapi.testclient import TestClient

from app.cmd.http import app
from app.infrastructure.factory_bot.user import get_token_for_normal_user


class APIClient:
    def __init__(self, _app, token):
        self.client = TestClient(_app)
        self.token = token

    def _make_request(self, method, url, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers
        return getattr(self.client, method)(url, **kwargs)

    def get(self, url, **kwargs):
        return self._make_request("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self._make_request("post", url, **kwargs)

    def put(self, url, **kwargs):
        return self._make_request("put", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._make_request("patch", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._make_request("delete", url, **kwargs)


client = APIClient(app, get_token_for_normal_user())
