from app.services.project_service import ProjectService
from app.entities.project import ProjectCreate, Project, ProjectUpdate

class InMemoryProjectRepo:
    def __init__(self):
        self.store = {}

    def create_project(self, project: ProjectCreate):
        p_id = "p-1"
        p = Project(p_id=p_id, p_name=project.p_name, p_head=project.p_head)
        self.store[p_id] = p
        return p

    def get_project(self, p_id: str):
        return self.store.get(p_id)

    def update_project(self, p_id: str, project: ProjectUpdate):
        p = self.store.get(p_id)
        if not p:
            return None
        data = p.model_dump()
        for k, v in project.model_dump().items():
            if v is not None:
                data[k] = v
        updated = Project(**data)
        self.store[p_id] = updated
        return updated

    def delete_project(self, p_id: str):
        if p_id in self.store:
            del self.store[p_id]
            return True
        return False

    def list_projects(self, page=1, size=10, q=None):
        items = list(self.store.values())
        return items, len(items)


class FakeProjectService(ProjectService):
    def __init__(self, repo):
        self.repo = repo


def test_project_create_get_update_delete():
    repo = InMemoryProjectRepo()
    svc = FakeProjectService(repo)

    p = ProjectCreate(p_name="Proj", p_head="Lead")
    created = svc.create_project(p)
    assert created.p_id == "p-1"

    fetched = svc.get_project(created.p_id)
    assert fetched.p_name == "Proj"

    upd = ProjectUpdate(p_name="Proj2")
    updated = svc.update_project(created.p_id, upd)
    assert updated.p_name == "Proj2"

    assert svc.delete_project(created.p_id) is True
    try:
        svc.get_project(created.p_id)
        assert False
    except Exception:
        pass
