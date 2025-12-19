"""Business logic for project management.

This module exposes a `ProjectService` responsible for creating,
updating, deleting and listing projects using the underlying
`ProjectRepository`.
"""

from ..repositories.project_repository import ProjectRepository
from ..config.database import Database
from ..entities.project import ProjectCreate, ProjectUpdate, ProjectResponse
from typing import List, Optional, Tuple
from ..exceptions import NotFoundError

class ProjectService:
    """Service layer handling project operations."""

    def __init__(self, db: Database):
        """Initialize the service with a database wrapper."""
        self.repo = ProjectRepository(db)

    def create_project(self, project: ProjectCreate) -> ProjectResponse:
        """Create a new project and return a `ProjectResponse`."""
        p = self.repo.create_project(project)
        return ProjectResponse(**p.model_dump())

    def update_project(self, p_id: str, project: ProjectUpdate) -> ProjectResponse:
        """Update project `p_id` and return the updated object.

        Raises `NotFoundError` if the project does not exist or no
        modifications were made.
        """
        updated = self.repo.update_project(p_id, project)
        if updated is None:
            raise NotFoundError(f"Project with id {p_id} not found or no changes provided")
        return ProjectResponse(**updated.model_dump())

    def delete_project(self, p_id: str) -> bool:
        """Delete project by id, raising `NotFoundError` if not found."""
        success = self.repo.delete_project(p_id)
        if not success:
            raise NotFoundError(f"Project with id {p_id} not found")
        return True

    def get_project(self, p_id: str) -> ProjectResponse:
        """Return a project by id or raise `NotFoundError`."""
        p = self.repo.get_project(p_id)
        if p is None:
            raise NotFoundError(f"Project with id {p_id} not found")
        return ProjectResponse(**p.model_dump())

    def list_projects(self, page: int = 1, size: int = 10, q: Optional[str] = None) -> Tuple[List[ProjectResponse], int]:
        """Return paginated projects, optional `q` for searching by id/name."""
        items, total = self.repo.list_projects(page=page, size=size, q=q)
        return [ProjectResponse(**p.model_dump()) for p in items], total
