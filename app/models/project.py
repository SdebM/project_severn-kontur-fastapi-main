from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import table
from sqlmodel import SQLModel, Field, Relationship

class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=120, min_length=3)
    description: Optional[str] = Field(default=None)
    owner_id: int = Field(foreign_key="users.id")

    owner: "User" = Relationship(back_populates="owner_projects")


if TYPE_CHECKING:
    from app.models.user import User
