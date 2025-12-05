from ..repositories.project_repository import ProjectRepository
from ..config.database import Database
from ..entities.project import ProjectCreate, ProjectUpdate, Project
from typing import List, Optional

class ProjectService:
    def __init__(self, db: Database):
        self.repo = ProjectRepository(db)

    def create_project(self, project: ProjectCreate) -> Project:
        return self.repo.create_project(project)

    def update_project(self, p_id: str, project: ProjectUpdate) -> Optional[Project]:
        return self.repo.update_project(p_id, project)

    def delete_project(self, p_id: str) -> bool:
        return self.repo.delete_project(p_id)

    def get_project(self, p_id: str) -> Optional[Project]:
        return self.repo.get_project(p_id)

    def list_projects(self) -> List[Project]:
        return self.repo.list_projects()
