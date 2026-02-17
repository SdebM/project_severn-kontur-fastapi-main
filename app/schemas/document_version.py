from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DocumentVersionBase(BaseModel):
    version: int
    content_snapshot: str

class DocumentVersionRead(DocumentVersionBase):
    id: int
    document_id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentVersionReadWithCreator(DocumentVersionRead):
    creator_email: Optional[str] = None