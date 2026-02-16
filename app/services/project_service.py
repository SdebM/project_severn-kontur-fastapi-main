from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.core.audit import log_action
from app.core.permissions import can_manage_project, can_view_project
from app.models.audit_log import EntityType
from app.models.project import Project
from app.models.project_access import ProjectAccess
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.session.get(Project, project_id)
    
    def create_project(self,  project_data: ProjectCreate, owner: User) -> Project:
        
        project = Project(
            title=project_data.title,
            description=project_data.description,
            owner_id=owner.id
        )
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)

        log_action(
            session=self.session,
            user_id=owner.id,
            action="create_project",
            entity_type=EntityType.project,
            entity_id=project.id,
            meta={"title": project.title}
        )
        
        return project
    
    def list_projects(self, user: User, skip: int = 0, limit: int = 20) -> list[Project]:
        if user.role == UserRole.admin:
            statement = select(Project).offset(skip).limit(limit)
            return list(self.session.exec(statement).all())
        
        owned_statement = select(Project).where(Project.owner_id == user.id)
        owned_projects = self.session.exec(owned_statement).all()
        owned_ids = {p.id for p in owned_projects}


        access_statement = select(ProjectAccess).where(ProjectAccess.user_id == user.id)
        accesses = self.session.exec(access_statement).all()
        access_project_ids = {a.project_id for a in accesses}


        all_project_ids = owned_ids | access_project_ids
        
        if not all_project_ids:
            return []
        
        statement = select(Project).where(
            Project.id.in_(all_project_ids)
        ).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_project(self, project_id: int, user: User) -> Project:
        project = self.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Project not found"
            )
        
        if not can_view_project(self.session, user, project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        return project
    
    def update_project(self, project_id: int, project_data: ProjectUpdate, user: User) -> Project:
        project = self.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not can_manage_project(self.session, user, project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin or project owner can update"
            )
        
        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)

        log_action(
            session=self.session,
            user_id=user.id,
            action="update_project",
            entity_type=EntityType.project,
            entity_id=project.id,
            meta={"updated_fields": list(update_data.keys())}
        )
        
        return project
    
    


    



    
