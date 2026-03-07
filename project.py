from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    image: str
    tags: List[str] = []
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    featured: bool = False
    order: int = 0


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    image: Optional[str] = None
    tags: Optional[List[str]] = None
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    featured: Optional[bool] = None
    order: Optional[int] = None

