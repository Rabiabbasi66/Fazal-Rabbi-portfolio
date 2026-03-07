from pydantic import BaseModel, Field, ConfigDict, BeforeValidator # Add BeforeValidator
from typing import Optional, List, Annotated # Add Annotated
from datetime import datetime

# This helper converts MongoDB ObjectIds to strings automatically
PyObjectId = Annotated[str, BeforeValidator(str)]

class SkillItem(BaseModel):
    name: str
    level: int = Field(..., ge=0, le=100)

class SkillBase(BaseModel):
    category: str = Field(..., min_length=2, max_length=50)
    icon: str = Field(..., min_length=2, max_length=50)
    color: str = Field(default="from-blue-500 to-cyan-500")
    skills: List[SkillItem] = []
    order: int = 0

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    # Use the PyObjectId helper here
    id: PyObjectId = Field(alias="_id") 
    
    # Optional prevents crashes if dates are missing in MongoDB
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class SkillUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    icon: Optional[str] = Field(None, min_length=2, max_length=50)
    color: Optional[str] = None
    skills: Optional[List[SkillItem]] = None
    order: Optional[int] = None