from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ServiceBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    icon: str = Field(..., min_length=2, max_length=50)
    color: str = Field(default="from-blue-500 to-cyan-500")
    features: List[str] = []
    order: int = 0


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    icon: Optional[str] = Field(None, min_length=2, max_length=50)
    color: Optional[str] = None
    features: Optional[List[str]] = None
    order: Optional[int] = None
