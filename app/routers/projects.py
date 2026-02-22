from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session

from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService
from app.models.user import User
from app.db.session import get_session
from app.core.security import get_current_user, require_roles


router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, session: Session = Depends(get_session), current_user: User = Depends(require_roles("admin", "manager"))):
    service = ProjectService(session)
    return service.create_project(project_data, current_user)

@router.get("/", response_model=List[ProjectRead])
def list_projects( skip: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)):

    service = ProjectService(session)
    return service.list_projects(current_user, skip, limit)

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    service = ProjectService(session)
    return service.get_project(project_id, current_user)

@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    service = ProjectService(session)
    return service.update_project(project_id, project_data, current_user)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles("admin", "manager"))
):
    service = ProjectService(session)
    service.delete_project(project_id, current_user)


