from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True) # Unique ID for compatibility with frontend expectations
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    display_name = Column(String)
    role = Column(String) # principal, teacher, student, parent
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    school = relationship("School", back_populates="users", foreign_keys=[school_id])

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
    # For a real LMS, we'd have a many-to-many relationship for students, 
    # but for simplicity let's stick to simple schemas or a separate table for enrollment.
