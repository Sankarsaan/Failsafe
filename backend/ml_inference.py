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
feature_names = None

def load_models():
    global model, explainer, feature_names
    if model is None or explainer is None or feature_names is None:
        model_path = os.path.join(BASE_DIR, "por_student_model.pkl")
        explainer_path = os.path.join(BASE_DIR, "por_shap_explainer.pkl")
        feature_names_path = os.path.join(BASE_DIR, "por_feature_names.pkl")
        if os.path.exists(model_path) and os.path.exists(explainer_path) and os.path.exists(feature_names_path):
            model = joblib.load(model_path)
            explainer = joblib.load(explainer_path)
            feature_names = joblib.load(feature_names_path)
        else:
            raise Exception("Model files not found. Run train_model.py first.")

import re

PREFIX_MAP = {
    "cse": "cs",
    "mnc": "ma",
    "electrical": "ee",
    "dsai": "da",
    "mechanical": "me",
    "chemical": "ce",
    "civil": "cl"
}

def process_csv(file_path: str, db: Session, current_user: models.User):
    load_models()
    df = pd.read_csv(file_path)
    
    if 'course_id' not in df.columns:
        raise ValueError("Missing course_id column in CSV")

    from sqlalchemy import func

    unique_courses = df['course_id'].dropna().unique()
    for cid in unique_courses:
        cid_str = str(cid).strip()

        # Case-insensitive lookup — CS201, cs201, Cs201 all work
        course = db.query(models.Course).filter(
            func.upper(models.Course.course_id) == cid_str.upper()
        ).first()

        if not course:
            raise ValueError(f"Course '{cid_str}' does not exist in the system. Please contact the institute to add it.")
        if course.faculty_id is None:
            raise ValueError(f"Course '{cid_str}' has not been assigned to any faculty yet. Please wait for HOD approval.")
        if course.faculty_id != current_user.id:
            raise ValueError(f"Course '{cid_str}' is not assigned to you. You can only upload data for your own courses.")

    categorical_features = ['famsup', 'higher', 'internet', 'address', 'activities', 'romantic', 'sup_paid']
    numeric_features = ['absentness', 'past_failures', 'study_time', 'health', 'Pjob', 'Pedu', 'famrel', 'Alc', 'unstructured_time']
    features = categorical_features + numeric_features
    X = df[features]
    
    probs = model.predict_proba(X)
    
    y_pred_custom = []
    for p in probs:
        if p[2] > 0.25:
            y_pred_custom.append(2)
        else:
            if p[1] >= p[0]:
                y_pred_custom.append(1)
            else:
                y_pred_custom.append(0)
    preds = np.array(y_pred_custom)
    
    X_transformed = model.named_steps['preprocessor'].transform(X)
    shap_values = explainer.shap_values(X_transformed)
    
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
                roll_number=str(row.get('roll_number', ''))
            )
            db.add(student)
            db.flush()
            
        course_id = str(row.get('course_id'))
        takes_record = db.query(models.Takes).filter(models.Takes.student_id == student_id, models.Takes.course_id == course_id).first()
        if not takes_record:
            takes_record = models.Takes(student_id=student_id, course_id=course_id)
            db.add(takes_record)
            
        db.query(models.PerformanceRecord).filter(models.PerformanceRecord.student_id == student_id).delete()
        
        perf_data = {}
        for f in features:
            val = row[f]
            if pd.isna(val):
                perf_data[f] = None
            elif isinstance(val, (np.integer, int)):
                perf_data[f] = int(val)
            elif isinstance(val, (np.floating, float)):
                perf_data[f] = float(val)
            else:
                perf_data[f] = str(val)

        perf_record = models.PerformanceRecord(
            student_id=student_id,
            performance_data=perf_data
        )
        db.add(perf_record)
        
        db.query(models.RiskPrediction).filter(models.RiskPrediction.student_id == student_id).delete()
        
        shap_summary = {str(feature_names[j]): float(shap_vals_high_risk[i][j]) for j in range(len(feature_names))}
        
        risk_pred = models.RiskPrediction(
            student_id=student_id,
            risk_score=float(probs[i][2]), 
            risk_level=risk_mapping[int(preds[i])],
            shap_summary=shap_summary
        )
        db.add(risk_pred)
        
    db.commit()
