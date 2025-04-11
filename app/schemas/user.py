from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties for OAuth sign-in
class UserCreateOAuth(UserBase):
    google_oauth_id: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class User(UserInDBBase):
    pass

# Properties stored in DB
class UserInDB(UserInDBBase):
    password_hash: str 