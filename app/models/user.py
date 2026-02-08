from datetime import datetime, timezone 
from typing import Optional, TYPE_CHECKING
from enum import Enum 
from sqlmodel import SQLModel, Field, Relationship


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    worker = "worker"
    viewer = "viewer"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.viewer)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    owner_projects: list["Project"] = Relationship(back_populates="owner")

if TYPE_CHECKING:
    from app.models.project import Project


