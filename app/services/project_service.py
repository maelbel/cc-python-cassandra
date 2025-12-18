from ..repositories.project_repository import ProjectRepository
from ..config.database import Database
from ..entities.project import ProjectCreate, ProjectUpdate, Project, ProjectResponse
from typing import List, Optional, Tuple
from ..exceptions import NotFoundError


class ProjectService:
    def __init__(self, db: Database):
        self.repo = ProjectRepository(db)

    def create_project(self, project: ProjectCreate) -> ProjectResponse:
        p = self.repo.create_project(project)
        return ProjectResponse(**p.model_dump())

    def update_project(self, p_id: str, project: ProjectUpdate) -> ProjectResponse:
        updated = self.repo.update_project(p_id, project)
        if updated is None:
            raise NotFoundError(f"Project with id {p_id} not found or no changes provided")
        return ProjectResponse(**updated.model_dump())

    def delete_project(self, p_id: str) -> bool:
        success = self.repo.delete_project(p_id)
        if not success:
            raise NotFoundError(f"Project with id {p_id} not found")
        return True

    def get_project(self, p_id: str) -> ProjectResponse:
        p = self.repo.get_project(p_id)
        if p is None:
            raise NotFoundError(f"Project with id {p_id} not found")
        return ProjectResponse(**p.model_dump())

    def list_projects(self, page: int = 1, size: int = 10, q: str | None = None) -> Tuple[List[ProjectResponse], int]:
        items, total = self.repo.list_projects(page=page, size=size, q=q)
        return [ProjectResponse(**p.model_dump()) for p in items], total
