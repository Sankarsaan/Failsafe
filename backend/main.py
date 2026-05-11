import os
import json
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict, Any

import models, schemas, auth, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FAILSAFE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        department=models.DepartmentEnum(user.department),
        role=models.RoleEnum.faculty,
        status=models.StatusEnum.pending
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Registration submitted for HOD approval."}

@app.post("/api/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if user.status == models.StatusEnum.pending:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending HOD approval."
        )
    
    access_token = auth.create_access_token(data={
        "sub": user.email,
        "role": user.role.value,
        "status": user.status.value,
        "department": user.department.value
    })
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/admin/pending-faculty", response_model=List[schemas.UserResponse])
def get_pending_faculty(current_hod: models.User = Depends(auth.get_current_hod), db: Session = Depends(database.get_db)):
    pending_users = db.query(models.User).filter(
        models.User.department == current_hod.department,
        models.User.status == models.StatusEnum.pending,
        models.User.role == models.RoleEnum.faculty
    ).all()
    return pending_users

@app.post("/api/admin/approve-faculty/{user_id}")
def approve_faculty(user_id: int, current_hod: models.User = Depends(auth.get_current_hod), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.department != current_hod.department:
        raise HTTPException(status_code=403, detail="Cannot approve faculty from another department")
        
    user.status = models.StatusEnum.approved
    db.commit()
    return {"message": f"User {user.email} approved successfully."}

@app.get("/api/dashboard")
def get_dashboard(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    dept = current_user.department.value
    total_students = db.query(models.Student).filter(models.Student.major == dept).count()
    
    high_risk = db.query(models.RiskPrediction).join(models.Student).filter(
        models.Student.major == dept,
        models.RiskPrediction.risk_level == "High"
    ).count()
    
    # Mock active interventions for now
    active_interventions = 8
    
    # Calculate Risk Distribution
    moderate_risk = db.query(models.RiskPrediction).join(models.Student).filter(
        models.Student.major == dept,
        models.RiskPrediction.risk_level == "Moderate"
    ).count()
    
    low_risk = db.query(models.RiskPrediction).join(models.Student).filter(
        models.Student.major == dept,
        models.RiskPrediction.risk_level == "Low"
    ).count()
    
    risk_distribution = [
        {"name": "High Risk", "value": high_risk, "color": "#ef4444"},
        {"name": "Moderate Risk", "value": moderate_risk, "color": "#f59e0b"},
        {"name": "Low Risk", "value": low_risk, "color": "#10b981"},
    ]
    
    # Mock trends
    trend_data = [
        {"name": "Week 1", "riskScore": 12},
        {"name": "Week 2", "riskScore": 15},
        {"name": "Week 3", "riskScore": 18},
        {"name": "Week 4", "riskScore": 25},
        {"name": "Week 5", "riskScore": 22},
        {"name": "Week 6", "riskScore": 30},
        {"name": "Week 7", "riskScore": 28},
    ]

    return {
        "total_students": total_students,
        "high_risk": high_risk,
        "active_interventions": active_interventions,
        "distribution": risk_distribution,
        "trends": trend_data
    }

@app.get("/api/students")
def get_students(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    dept = current_user.department.value
    students = db.query(models.Student).filter(models.Student.major == dept).all()
    results = []
    for s in students:
        record = db.query(models.PerformanceRecord).filter(models.PerformanceRecord.student_id == s.id).first()
        prediction = db.query(models.RiskPrediction).filter(models.RiskPrediction.student_id == s.id).first()
        
        results.append({
            "id": s.id,
            "name": s.name,
            "attendance": f"{int(record.performance_data.get('attendance_rate', 0) * 100)}%" if record and record.performance_data else "N/A",
            "grade": "C" if record and record.performance_data and record.performance_data.get('midterm_score', 0) < 60 else "A", 
            "riskLevel": prediction.risk_level if prediction else "Unknown"
        })
    return results

@app.get("/api/students/{id}")
def get_student_detail(id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    dept = current_user.department.value
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if student.major != dept:
        raise HTTPException(status_code=403, detail="Access denied. Student belongs to another department.")
        
    prediction = db.query(models.RiskPrediction).filter(models.RiskPrediction.student_id == id).first()
    
    shap_data = []
    if prediction and prediction.shap_summary:
        for feature, impact in prediction.shap_summary.items():
            color = "#ef4444" if impact > 0 else "#10b981" # Red if increases risk, Emerald if decreases
            shap_data.append({"feature": feature, "impact": impact, "color": color})
            
    return {
        "id": student.id,
        "name": student.name,
        "major": student.major,
        "year": student.year,
        "riskScore": int(prediction.risk_score * 100) if prediction else 0,
        "riskLevel": prediction.risk_level if prediction else "Unknown",
        "shapData": shap_data
    }

@app.post("/api/upload")
async def upload_data(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    from ml_inference import process_csv
    import tempfile
    import os
    
    fd, temp_file_path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
        
    try:
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())
            
        process_csv(temp_file_path, db)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return {"message": "Upload and processing successful"}
