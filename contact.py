from pydantic import BaseModel, EmailStr, Field, ConfigDict, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime

# Convert MongoDB ObjectId to string automatically
PyObjectId = Annotated[str, BeforeValidator(str)]

class ContactBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)

class ContactResponse(ContactBase):
    # Fix for image_29b295.png (id mapping)
    id: PyObjectId = Field(alias="_id")
    status: str = "unread"
    
    # Fix for image_29c0de.png (missing fields crash)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    status: Optional[str] = None