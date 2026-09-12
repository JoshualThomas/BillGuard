from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    icon: str = "folder"
    color: str = "#6366F1"


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: UUID
    user_id: Optional[UUID] = None
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
