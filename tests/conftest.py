"""Common pytest fixtures."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


class _FakeResponse:
    def __init__(self, json_data=None, content=b"", status_code=200):
        self._json = json_data
        self.content = content
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):  # noqa: D401
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture()
def fake_session(monkeypatch):
    """Patch `requests.Session` with a controllable fake."""

    captured = SimpleNamespace(last_request=None)

    class FakeSession:
        def __init__(self):
            self.headers = {}

        def get(self, url):
            captured.last_request = ("GET", url)
            if url.endswith("/TTS/GetSpeaker"):
                return _FakeResponse(json_data=[{"name": "佑希"}])
            if url.endswith("/Key/Usage"):
                return _FakeResponse(json_data={"quota": 100, "remaining": 99})
            return _FakeResponse(status_code=404)

        def post(self, url, json, headers):  # noqa: D401
            captured.last_request = ("POST", url, json, headers)
            return _FakeResponse(content=b"WAVDATA")

    monkeypatch.setattr("voai_client.requests.Session", FakeSession)
    return captured