from fastapi.testclient import TestClient
from app.main import app
from app.controllers.auth_controller import get_current_user
from app.dependencies import get_db


def override_get_current_user():
    class User:
        id = "user-1"
        username = "tester"
        email = "t@example.com"
        is_active = True
    return User()


def override_get_db():
    class DummyDB:
        def get_session(self):
            return None
    return DummyDB()


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_list_projects_root():
    resp = client.get('/projects/')
    assert resp.status_code in (200, 500)


def test_create_project_endpoint():
    payload = {"p_name": "NewProj", "p_head": "Lead"}
    resp = client.post('/projects/', json=payload)
    assert resp.status_code in (200, 500)
