"""Repository implementation for project CRUD operations using Cassandra."""

from cassandra.query import SimpleStatement
from ..entities.project import Project, ProjectCreate, ProjectUpdate
from ..config.database import Database
import uuid
from typing import List, Optional, Tuple
from .base import BaseRepository

class ProjectRepository(BaseRepository):
    """Encapsulates Cassandra queries for the `projects` table."""

    def __init__(self, db: Database):
        super().__init__(db)
        self.table = "projects"
        self.select_cols = "p_id, p_name, p_head"
        self.prefix = "p"

    def create_project(self, project: ProjectCreate) -> Project:
        """Insert a new project and return the created `Project` model."""
        project_id = str(uuid.uuid4())
        query = SimpleStatement("""
        INSERT INTO projects (p_id, p_name, p_head)
        VALUES (%s, %s, %s)
        """)
        self._get_session().execute(query, (project_id, project.p_name, project.p_head))
        return Project(p_id=project_id, p_name=project.p_name, p_head=project.p_head)

    def update_project(self, p_id: str, project: ProjectUpdate) -> Optional[Project]:
        """Apply partial updates to a project and return the updated model.

        Returns `None` when the provided `project` contains no changes.
        """
        sets = []
        params = []
        if project.p_name is not None:
            sets.append("p_name = %s")
            params.append(project.p_name)
        if project.p_head is not None:
            sets.append("p_head = %s")
            params.append(project.p_head)
        if not sets:
            return None
        set_clause = ", ".join(sets)
        query = SimpleStatement(f"UPDATE projects SET {set_clause} WHERE p_id = %s")
        params.append(p_id)
        self._get_session().execute(query, tuple(params))
        return self.get_project(p_id)

    def delete_project(self, p_id: str) -> bool:
        """Delete the project with the given id. Returns True on success."""
        query = SimpleStatement("DELETE FROM projects WHERE p_id = %s")
        self._get_session().execute(query, (p_id,))
        return True

    def get_project(self, p_id: str) -> Optional[Project]:
        """Fetch a single project by id and return a `Project` model or None."""
        query = SimpleStatement("SELECT p_id, p_name, p_head FROM projects WHERE p_id = %s")
        result = self._get_session().execute(query, (p_id,))
        row = result.one()
        if row:
            return Project(p_id=row.p_id, p_name=row.p_name, p_head=row.p_head)
        return None

    def list_projects(self, page: int = 1, size: int = 10, q: Optional[str] = None) -> Tuple[List[Project], int]:
        """Return a paginated list of projects and the total count.

        Search by `q` is delegated to `BaseRepository.list_with_search`.
        """
        rows, total = self.list_with_search(
            page=page,
            size=size,
            q=q,
            filters=None,
        )

        projects = [Project(p_id=row.p_id, p_name=row.p_name, p_head=row.p_head) for row in rows]

        return projects, total
