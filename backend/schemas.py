from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    role: str
    status: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StudentBase(BaseModel):
    id: str
    name: str
    major: str
    year: str

class StudentResponse(StudentBase):
    class Config:
        from_attributes = True

class RiskPredictionResponse(BaseModel):
    risk_score: float
    risk_level: str
    shap_summary: Dict[str, float]
    class Config:
        from_attributes = True

class StudentDetailResponse(StudentResponse):
    attendance: str 
    current_grade: str 
    risk_prediction: Optional[RiskPredictionResponse] = None
