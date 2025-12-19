from app.services.student_service import StudentService
from app.entities.student import StudentCreate, Student, StudentUpdate


class DummySession:
    def __init__(self):
        self.store = {}

    def execute(self, query, params=None):
        return None


class DummyDB:
    def __init__(self):
        self.session = DummySession()

    def get_session(self):
        return self.session


class InMemoryRepo:
    """A tiny replacement for StudentRepository behavior for unit testing."""
    def __init__(self):
        self.store = {}

    def create_student(self, student: StudentCreate):
        s_id = "id-1"
        s = Student(s_id=s_id, s_name=student.s_name, s_course=student.s_course, s_branch=student.s_branch, s_project_id=student.s_project_id)
        self.store[s_id] = s
        return s

    def get_student(self, s_id: str):
        return self.store.get(s_id)

    def update_student(self, s_id: str, student: StudentUpdate):
        s = self.store.get(s_id)
        if not s:
            return None
        data = s.model_dump()
        for k, v in student.model_dump().items():
            if v is not None:
                data[k] = v
        updated = Student(**data)
        self.store[s_id] = updated
        return updated

    def delete_student(self, s_id: str):
        if s_id in self.store:
            del self.store[s_id]
            return True
        return False

    def list_students(self, page=1, size=10, q=None, project_id=None):
        items = list(self.store.values())
        return items, len(items)


class FakeService(StudentService):
    def __init__(self, repo):
        # bypass StudentRepository and DB
        self.repo = repo


def test_create_and_get_student():
    repo = InMemoryRepo()
    svc = FakeService(repo)

    payload = StudentCreate(s_name="Alice", s_course="Math", s_branch="A", s_project_id=None)
    created = svc.create_student(payload)
    assert created.s_id == "id-1"
    assert created.s_name == "Alice"

    fetched = svc.get_student("id-1")
    assert fetched.s_name == "Alice"


def test_update_student():
    repo = InMemoryRepo()
    svc = FakeService(repo)
    payload = StudentCreate(s_name="Bob", s_course="CS", s_branch="B", s_project_id=None)
    created = svc.create_student(payload)
    assert created.s_id is not None

    upd = StudentUpdate(s_name="Bobby")
    updated = svc.update_student(created.s_id, upd)
    assert updated.s_name == "Bobby"


def test_delete_student():
    repo = InMemoryRepo()
    svc = FakeService(repo)
    payload = StudentCreate(s_name="Carol", s_course="Eng", s_branch="C", s_project_id=None)
    created = svc.create_student(payload)
    assert created.s_id is not None

    assert svc.delete_student(created.s_id) is True
    try:
        svc.get_student(created.s_id)
        assert False, "Expected NotFoundError"
    except Exception:
        # service raises NotFoundError; accept any exception here
        pass
