from datetime import datetime, datetitme, timezone 
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship


class DocumentStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    title: str = Field(max_length=120, min_length=3)
    content: Optional[str] = Field(default="")
    status: DocumentStatus = Field(default=DocumentStatus.draft)
    created_by: int = Field(foreign_key="users.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))
