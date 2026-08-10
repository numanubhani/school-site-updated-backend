from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    role: str

class UserCreate(UserBase):
    password: str
    school_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    uid: str
    school_id: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True

class SchoolBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None

class SchoolCreate(SchoolBase):
    pass

class SchoolResponse(SchoolBase):
    id: int
    invite_code: str
    principal_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ClassBase(BaseModel):
    name: str

class ClassCreate(ClassBase):
    teacher_id: Optional[int] = None

class ClassResponse(ClassBase):
    id: int
    school_id: int
    teacher_id: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
