import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DEPLOYGUARD_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("DEPLOYGUARD_API_TOKEN", "test-token")
    monkeypatch.setenv("GIT_SHA", "abc1234")
    monkeypatch.setenv("CI_TEST_STATUS", "passed")
    from app.main import app

    with TestClient(app) as c:  # context manager runs the lifespan (DB init)
        yield c
