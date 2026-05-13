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
    
    # Check if faculty exists in course table
    course_match = db.query(models.Course).filter(
        models.Course.instructor_faculty_id == user.faculty_id,
        models.Course.instructor_name == user.name
    ).first()

    if not course_match:
        raise HTTPException(status_code=400, detail="Registration failed: Name and Faculty ID not found in assigned courses. Please contact the institute.")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        faculty_id_str=user.faculty_id,
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
        
    if user.role != models.RoleEnum.admin and form_data.client_id and user.faculty_id_str != form_data.client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Faculty ID",
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
    
    # Map courses to this faculty
    courses_to_update = db.query(models.Course).filter(
        models.Course.instructor_faculty_id == user.faculty_id_str,
        models.Course.instructor_name == user.name
    ).all()
    
    for course in courses_to_update:
        course.faculty_id = user.id

    db.commit()
    return {"message": f"User {user.email} approved successfully and assigned to {len(courses_to_update)} courses."}

@app.get("/api/dashboard")
def get_dashboard(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    user_courses = [c.course_id for c in current_user.courses]
    
    total_students = db.query(models.Takes.student_id).filter(models.Takes.course_id.in_(user_courses)).distinct().count()
    
    high_risk = db.query(models.RiskPrediction.student_id).join(models.Takes, models.Takes.student_id == models.RiskPrediction.student_id).filter(
        models.Takes.course_id.in_(user_courses),
        models.RiskPrediction.risk_level == "High"
    ).distinct().count()
    
    active_interventions = 8
    
    moderate_risk = db.query(models.RiskPrediction.student_id).join(models.Takes, models.Takes.student_id == models.RiskPrediction.student_id).filter(
        models.Takes.course_id.in_(user_courses),
        models.RiskPrediction.risk_level == "Moderate"
    ).distinct().count()
    
    low_risk = db.query(models.RiskPrediction.student_id).join(models.Takes, models.Takes.student_id == models.RiskPrediction.student_id).filter(
        models.Takes.course_id.in_(user_courses),
        models.RiskPrediction.risk_level == "Low"
    ).distinct().count()
    
    risk_distribution = [
        {"name": "High Risk", "value": high_risk, "color": "#ef4444"},
        {"name": "Moderate Risk", "value": moderate_risk, "color": "#f59e0b"},
        {"name": "Low Risk", "value": low_risk, "color": "#10b981"},
    ]
    
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
    courses = [c.course_id for c in current_user.courses]
    students_with_courses = db.query(models.Student, models.Takes.course_id).join(models.Takes).filter(models.Takes.course_id.in_(courses)).all()
    
    results = []
    for s, course_id in students_with_courses:
        record = db.query(models.PerformanceRecord).filter(models.PerformanceRecord.student_id == s.id).first()
        prediction = db.query(models.RiskPrediction).filter(models.RiskPrediction.student_id == s.id).first()
        
        results.append({
            "id": s.id,
            "name": s.name,
            "courseId": course_id,
            "absences": str(int(record.performance_data.get('absentness', 0))) if record and record.performance_data and record.performance_data.get('absentness') is not None else "N/A",
            "pastFailures": str(int(record.performance_data.get('past_failures', 0))) if record and record.performance_data and record.performance_data.get('past_failures') is not None else "N/A", 
            "riskLevel": prediction.risk_level if prediction else "Unknown"
        })
    return results

def format_feature_name(raw_name: str) -> str:
    name = raw_name.replace("remainder__", "").replace("cat__", "")
    mapping = {
        "absentness": "Absences",
        "past_failures": "Past Failures",
        "study_time": "Study Time",
        "health": "Health",
        "Pjob": "Parents Job Status",
        "Pedu": "Parents Education",
        "famrel": "Family Relationship",
        "Alc": "Alcohol Consumption",
        "unstructured_time": "Free Time",
        "famsup_yes": "Has Family Support",
        "famsup_no": "No Family Support",
        "higher_yes": "Wants Higher Education",
        "higher_no": "No Higher Ed Goals",
        "internet_yes": "Has Internet",
        "internet_no": "No Internet",
        "address_U": "Urban Address",
        "address_R": "Rural Address",
        "activities_yes": "Extracurriculars",
        "activities_no": "No Extracurriculars",
        "romantic_yes": "In Relationship",
        "romantic_no": "Not In Relationship",
        "sup_paid_yes_yes": "School & Paid Support",
        "sup_paid_no_no": "No External Support",
        "sup_paid_yes_no": "School Support Only",
        "sup_paid_no_yes": "Paid Support Only"
    }
    return mapping.get(name, name.replace("_", " ").title())

@app.get("/api/students/{id}")
def get_student_detail(id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    takes = db.query(models.Takes).filter(models.Takes.student_id == id).all()
    user_courses = [c.course_id for c in current_user.courses]
    if not any(t.course_id in user_courses for t in takes):
        raise HTTPException(status_code=403, detail="Access denied. Student is not in any of your courses.")
        
    prediction = db.query(models.RiskPrediction).filter(models.RiskPrediction.student_id == id).first()
    
    shap_data = []
    if prediction and prediction.shap_summary:
        for feature, impact in prediction.shap_summary.items():
            color = "#ef4444" if impact > 0 else "#10b981" # Red if increases risk, Emerald if decreases
            clean_name = format_feature_name(feature)
            shap_data.append({"feature": clean_name, "impact": impact, "color": color})
            
    return {
        "id": student.id,
        "name": student.name,
        "roll_number": student.roll_number,
        "riskScore": int(prediction.risk_score * 100) if prediction else 0,
        "riskLevel": prediction.risk_level if prediction else "Unknown",
        "shapData": shap_data
    }

@app.get("/api/my-courses")
def get_my_courses(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    courses = db.query(models.Course).filter(models.Course.faculty_id == current_user.id).all()
    return [{"course_id": c.course_id, "course_name": c.course_name} for c in courses]

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
            
        process_csv(temp_file_path, db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return {"message": "Upload and processing successful"}
