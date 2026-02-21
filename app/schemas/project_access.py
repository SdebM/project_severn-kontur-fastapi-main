from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.project_access import Permission


class ProjectAccessBase(BaseModel):
    user_id: int
    permission: Permission = Permission.viewer


class ProjectAccessCreate(ProjectAccessBase):
    pass 

class ProjectAccessRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    permission: Permission
    granted_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProjectAccessReadWithUser(ProjectAccessRead):
    user_email: Optional[str] = None
    granter_email: Optional[str] = None