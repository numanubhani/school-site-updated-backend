from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    display_name = Column(String)
    role = Column(String)  # principal, teacher, student, parent
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    school = relationship("School", back_populates="users", foreign_keys=[school_id])
    enrollments = relationship("Enrollment", back_populates="student", foreign_keys="Enrollment.student_id")

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    invite_code = Column(String, unique=True, index=True)
    principal_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    principal = relationship("User", foreign_keys=[principal_id])
    users = relationship("User", back_populates="school", foreign_keys=[User.school_id])
    classes = relationship("Class", back_populates="school")

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    school = relationship("School", back_populates="classes")
    teacher = relationship("User", foreign_keys=[teacher_id])
    subjects = relationship("Subject", back_populates="class_", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="class_", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("User", back_populates="enrollments", foreign_keys=[student_id])
    class_ = relationship("Class", back_populates="enrollments")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    class_ = relationship("Class", back_populates="subjects")
    created_by = relationship("User", foreign_keys=[created_by_id])
    materials = relationship("Material", back_populates="subject", cascade="all, delete-orphan")

class ParentStudent(Base):
    __tablename__ = "parent_students"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    material_type = Column(String)  # video_url, pdf, file
    url = Column(String, nullable=True)       # for video_url or served file path
    filename = Column(String, nullable=True)  # original filename
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    uploaded_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subject = relationship("Subject", back_populates="materials")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])

class PlatformCourse(Base):
    __tablename__ = "platform_courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    domain = Column(String)
    description = Column(Text)
    duration = Column(String)
    icon_name = Column(String)
    order = Column(Integer, default=0)

    materials = relationship("PlatformCourseMaterial", back_populates="course", cascade="all, delete-orphan")
    lessons = relationship("PlatformCourseLesson", back_populates="course", cascade="all, delete-orphan", order_by="PlatformCourseLesson.order")

class PlatformCourseMaterial(Base):
    __tablename__ = "platform_course_materials"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("platform_courses.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    material_type = Column(String)  # pdf, video_url, video, worksheet, file
    url = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    course = relationship("PlatformCourse", back_populates="materials")

class PlatformCourseLesson(Base):
    __tablename__ = "platform_course_lessons"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("platform_courses.id"))
    title = Column(String)
    content = Column(Text)
    duration = Column(String)
    order = Column(Integer, default=0)

    course = relationship("PlatformCourse", back_populates="lessons")
