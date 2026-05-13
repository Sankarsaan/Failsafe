from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
import database
import enum

Base = database.Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    faculty = "faculty"

class StatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"

class DepartmentEnum(str, enum.Enum):
    cse = "cse"
    mnc = "mnc"
    dsai = "dsai"
    mechanical = "mechanical"
    chemical = "chemical"
    civil = "civil"
    electrical = "electrical"

class Hod(Base):
    __tablename__ = "hods"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    department = Column(Enum(DepartmentEnum), unique=True) # Only one HOD per department

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id_str = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    department = Column(Enum(DepartmentEnum))
    role = Column(Enum(RoleEnum), default=RoleEnum.faculty)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)

    courses = relationship("Course", back_populates="faculty")

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(String(255), primary_key=True, index=True)
    course_name = Column(String(255), nullable=True)
    instructor_name = Column(String(255), nullable=True)
    instructor_faculty_id = Column(String(255), index=True, nullable=True)
    faculty_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    faculty = relationship("User", back_populates="courses")
    students = relationship("Student", secondary="takes", back_populates="courses")

class Takes(Base):
    __tablename__ = "takes"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), ForeignKey("students.id"))
    course_id = Column(String(255), ForeignKey("courses.course_id"))

class Student(Base):
    __tablename__ = "students"

    id = Column(String(255), primary_key=True, index=True) # e.g. STU-001
    name = Column(String(255), index=True)
    roll_number = Column(String(255), index=True, nullable=True)
    
    performance_records = relationship("PerformanceRecord", back_populates="student")
    risk_predictions = relationship("RiskPrediction", back_populates="student")
    courses = relationship("Course", secondary="takes", back_populates="students")

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), ForeignKey("students.id"))
    performance_data = Column(JSON)

    student = relationship("Student", back_populates="performance_records")

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), ForeignKey("students.id"))
    risk_score = Column(Float)
    risk_level = Column(String(255))
    shap_summary = Column(JSON)

    student = relationship("Student", back_populates="risk_predictions")
