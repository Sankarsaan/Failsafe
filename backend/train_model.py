import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
from sklearn.model_selection import train_test_split
import urllib.request
import zipfile
import os

def train_and_save_model():
    print("Loading UCIML Student Performance dataset...")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00320/student.zip"
    
    if not os.path.exists("student.zip"):
        urllib.request.urlretrieve(url, "student.zip")
    
    with zipfile.ZipFile("student.zip", 'r') as zip_ref:
        zip_ref.extractall("student_data")
        
    df = pd.read_csv("student_data/student-por.csv", sep=";")
    
    df['attendance_rate'] = 1 - (df['absences'] / df['absences'].max())
    df['midterm_score'] = df['G2'] / 20.0 * 100
    df['behavioral_score'] = (df['famrel'] + (5 - df['goout']) + (5 - df['Walc'])) / 15.0 * 100
    df['missed_assignments'] = df['failures']
    df['office_hours_visited'] = df['studytime']
    df['previous_gpa'] = df['G1'] / 20.0 * 4.0
    
    conditions = [
        (df['G3'] < 10),
        (df['G3'] >= 10) & (df['G3'] < 14),
        (df['G3'] >= 14)
    ]
    choices = [2, 1, 0] # High, Moderate, Low
    df['target'] = np.select(conditions, choices, default=0)
    
    features = ['attendance_rate', 'midterm_score', 'behavioral_score', 'missed_assignments', 'office_hours_visited', 'previous_gpa']
    X = df[features]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    model.fit(X_train, y_train)
    
    print("Initializing SHAP explainer...")
    explainer = shap.TreeExplainer(model)
    
    print("Saving model and explainer...")
    joblib.dump(model, "student_model.pkl")
    joblib.dump(explainer, "shap_explainer.pkl")
    
    print("Done! Model saved as student_model.pkl and explainer as shap_explainer.pkl")

if __name__ == "__main__":
    train_and_save_model()
