import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
from sqlalchemy.orm import Session
import models
import uuid
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Lazy loading of models to avoid crashing if files don't exist yet
model = None
explainer = None

def load_models():
    global model, explainer
    if model is None or explainer is None:
        model_path = os.path.join(BASE_DIR, "student_model.pkl")
        explainer_path = os.path.join(BASE_DIR, "shap_explainer.pkl")
        if os.path.exists(model_path) and os.path.exists(explainer_path):
            model = joblib.load(model_path)
            explainer = joblib.load(explainer_path)
        else:
            raise Exception("Model files not found. Run train_model.py first.")

def process_csv(file_path: str, db: Session):
    load_models()
    df = pd.read_csv(file_path)
    
    features = ['attendance_rate', 'midterm_score', 'behavioral_score', 'missed_assignments', 'office_hours_visited', 'previous_gpa']
    X = df[features]
    
    preds = model.predict(X)
    probs = model.predict_proba(X)
    
    shap_values = explainer.shap_values(X)
    
    if isinstance(shap_values, list):
        shap_vals_high_risk = shap_values[2]
    else:
        if len(shap_values.shape) == 3:
            shap_vals_high_risk = shap_values[:, :, 2]
        else:
            shap_vals_high_risk = shap_values
            
    risk_mapping = {0: "Low", 1: "Moderate", 2: "High"}
    
    for i, row in df.iterrows():
        student_id = str(row.get('id', f"STU-{uuid.uuid4().hex[:6].upper()}"))
        
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if not student:
            student = models.Student(
                id=student_id,
                name=row.get('name', 'Unknown'),
                major=row.get('major', 'Unknown'),
                year=row.get('year', 'Unknown')
            )
            db.add(student)
            
        db.query(models.PerformanceRecord).filter(models.PerformanceRecord.student_id == student_id).delete()
        
        perf_record = models.PerformanceRecord(
            student_id=student_id,
            performance_data={
                "attendance_rate": float(row['attendance_rate']),
                "midterm_score": float(row['midterm_score']),
                "behavioral_score": float(row['behavioral_score']),
                "missed_assignments": int(row['missed_assignments']),
                "office_hours_visited": int(row['office_hours_visited']),
                "previous_gpa": float(row['previous_gpa'])
            }
        )
        db.add(perf_record)
        
        db.query(models.RiskPrediction).filter(models.RiskPrediction.student_id == student_id).delete()
        
        shap_summary = {feature: float(shap_vals_high_risk[i][j]) for j, feature in enumerate(features)}
        
        risk_pred = models.RiskPrediction(
            student_id=student_id,
            risk_score=float(probs[i][2]), 
            risk_level=risk_mapping[int(preds[i])],
            shap_summary=shap_summary
        )
        db.add(risk_pred)
        
    db.commit()
