from cassandra.query import SimpleStatement
from ..entities.project import Project, ProjectCreate, ProjectUpdate
from ..config.database import Database
import uuid
from typing import List, Optional, Tuple

class ProjectRepository:
    def __init__(self, db: Database):
        self.db = db

    def _get_session(self):
        session = self.db.get_session()
        if session is None:
            raise RuntimeError("Database session is not available")
        return session

    def create_project(self, project: ProjectCreate) -> Project:
        project_id = str(uuid.uuid4())
        query = SimpleStatement("""
        INSERT INTO projects (p_id, p_name, p_head)
        VALUES (%s, %s, %s)
        """)
        self._get_session().execute(query, (project_id, project.p_name, project.p_head))
        return Project(p_id=project_id, p_name=project.p_name, p_head=project.p_head)

    def update_project(self, p_id: str, project: ProjectUpdate) -> Optional[Project]:
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
        query = SimpleStatement("DELETE FROM projects WHERE p_id = %s")
        self._get_session().execute(query, (p_id,))
        return True

    def get_project(self, p_id: str) -> Optional[Project]:
        query = SimpleStatement("SELECT p_id, p_name, p_head FROM projects WHERE p_id = %s")
        result = self._get_session().execute(query, (p_id,))
        row = result.one()
        if row:
            return Project(p_id=row.p_id, p_name=row.p_name, p_head=row.p_head)
        return None

    def list_projects(self, page: int = 1, size: int = 10, q: Optional[str] = None) -> Tuple[List[Project], int]:
        """
        Return a tuple of (projects, total_estimate).
        Note: Cassandra does not support OFFSET; to emulate paging we fetch `page*size` rows and slice client-side.
        Searching by name uses ALLOW FILTERING which can be inefficient for large datasets.
        """
        session = self._get_session()
        limit = page * size

        if q:
            # If q looks like a UUID or exact id search, try filtering by p_id first
            # Otherwise search by p_name using ALLOW FILTERING
            try:
                # Proper UUID check: try to parse q as a UUID
                uuid.UUID(q)
                query = SimpleStatement("SELECT p_id, p_name, p_head FROM projects WHERE p_id = %s")
                rows = session.execute(query, (q,))
                projects = [Project(p_id=row.p_id, p_name=row.p_name, p_head=row.p_head) for row in rows]
                total = len(projects)
                # apply paging on single-result set
                start = (page - 1) * size
                return projects[start:start+size], total
            except (ValueError, AttributeError):
                pass

            # fallback: search by name using ALLOW FILTERING
            query = SimpleStatement(f"SELECT p_id, p_name, p_head FROM projects WHERE p_name >= %s ALLOW FILTERING LIMIT {limit}")
            rows = session.execute(query, (q,))
        else:
            query = SimpleStatement(f"SELECT p_id, p_name, p_head FROM projects LIMIT {limit}")
            rows = session.execute(query)

        projects = [Project(p_id=row.p_id, p_name=row.p_name, p_head=row.p_head) for row in rows]

        # Emulate total as number of returned rows (not full table count)
        total = len(projects)

        start = (page - 1) * size
        return projects[start:start+size], total
