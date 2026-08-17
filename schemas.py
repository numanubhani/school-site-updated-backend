from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    role: str

class UserCreate(UserBase):
    password: str
    school_id: Optional[int] = None

class UserCreateWithCode(BaseModel):
    email: EmailStr
    display_name: str
    password: str
    invite_code: str

class UserResponse(UserBase):
    id: int
    uid: str
    school_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

class ClassBase(BaseModel):
    name: str

class ClassCreate(ClassBase):
    teacher_id: Optional[int] = None

class ClassResponse(ClassBase):
    id: int
    school_id: int
    teacher_id: Optional[int]
    created_at: datetime
    student_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    class_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    class_id: int
    created_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    material_type: str  # video_url, pdf, file
    url: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int
    filename: Optional[str]
    subject_id: int
    uploaded_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class PlatformCourseLessonResponse(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    duration: str
    order: int

    model_config = ConfigDict(from_attributes=True)

class PlatformCourseMaterialResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    material_type: str
    url: Optional[str]
    filename: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PlatformCourseResponse(BaseModel):
    id: int
    title: str
    domain: str
    description: str
    duration: str
    icon_name: str
    order: int
    materials: list[PlatformCourseMaterialResponse] = []
    lessons: list[PlatformCourseLessonResponse] = []

    model_config = ConfigDict(from_attributes=True)
