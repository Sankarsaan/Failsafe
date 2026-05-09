from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
import database
Base = database.Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    department = Column(String(255))

class Student(Base):
    __tablename__ = "students"

    id = Column(String(255), primary_key=True, index=True) # e.g. STU-001
    name = Column(String(255), index=True)
    major = Column(String(255))
    year = Column(String(255))
    
    performance_records = relationship("PerformanceRecord", back_populates="student")
    risk_predictions = relationship("RiskPrediction", back_populates="student")

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), ForeignKey("students.id"))
    performance_data = Column(JSON) # e.g. {"attendance_rate": 0.9, "midterm_score": 85.5, ...}

    student = relationship("Student", back_populates="performance_records")

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), ForeignKey("students.id"))
    risk_score = Column(Float)
    risk_level = Column(String(255)) # Low, Moderate, High
    shap_summary = Column(JSON) # {"Low Attendance": 0.45, ...}

    student = relationship("Student", back_populates="risk_predictions")
