import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report
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
 
    job_mapping = {'at_home': 0, 'other': 1, 'health': 1, 'services': 1, 'teacher': 2}
    df['Pjob'] = df['Mjob'].map(job_mapping) + df['Fjob'].map(job_mapping)
    df['Pedu'] = df['Medu'] + df['Fedu']
    df['Alc'] = df['Dalc'] + df['Walc']
    df['unstructured_time'] = df['goout'] + df['freetime']
    df['sup_paid'] = df['schoolsup'] + "_" + df['paid']
    df['absentness'] = df['absences']
    df['past_failures'] = df['failures']
    df['study_time'] = df['studytime']
 
    conditions = [
        (df['G3'] < 10),
        (df['G3'] >= 10) & (df['G3'] < 14),
        (df['G3'] >= 14)
    ]
    choices = [2, 1, 0] # High, Moderate, Low

    df['target'] = np.select(conditions, choices, default=0)
 
    categorical_features = ['famsup', 'higher', 'internet', 'address', 'activities', 'romantic', 'sup_paid']
    numeric_features = ['absentness', 'past_failures', 'study_time', 'health', 'Pjob', 'Pedu', 'famrel', 'Alc', 'unstructured_time']
    features = categorical_features + numeric_features

    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
    print("Setting up Pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'
    )
 
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42))
    ])
 
    print("Setting up RandomizedSearchCV...")
    param_distributions = {
        'classifier__max_depth': [3, 4, 5, 6, 8],
        'classifier__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'classifier__n_estimators': [50, 100, 200, 300],
        'classifier__subsample': [0.6, 0.8, 1.0],
        'classifier__colsample_bytree': [0.6, 0.8, 1.0]
    }
 
    random_search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_distributions,
        n_iter=20,
        scoring='f1_macro',
        cv=3,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
 
    print("Training XGBoost Pipeline with RandomizedSearchCV and Class Weights...")
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
    random_search.fit(X_train, y_train, classifier__sample_weight=sample_weights)
    print(f"Best parameters found: {random_search.best_params_}")
    best_pipeline = random_search.best_estimator_
    print("Evaluating Best Model with Custom Threshold (High Risk > 0.25)...")
    y_probs = best_pipeline.predict_proba(X_test)
 
    y_pred_custom = []
    for probs in y_probs:
        if probs[2] > 0.25:
            y_pred_custom.append(2)
        else:
            if probs[1] >= probs[0]:
                y_pred_custom.append(1)
            else:
                y_pred_custom.append(0)
    print(classification_report(y_test, y_pred_custom, target_names=['Low Risk', 'Moderate Risk', 'High Risk']))
 
    print("Initializing SHAP explainer...")
    xgb_model = best_pipeline.named_steps['classifier']
    explainer = shap.TreeExplainer(xgb_model)

    feature_names = best_pipeline.named_steps['preprocessor'].get_feature_names_out(features)
 
    print("Saving best model, explainer, and feature names...")
    joblib.dump(best_pipeline, "por_student_model.pkl")
    joblib.dump(explainer, "por_shap_explainer.pkl")
    joblib.dump(feature_names, "por_feature_names.pkl")
    joblib.dump(X_test, "por_X_test.pkl")
 
    print("Done! Model pipeline saved as por_student_model.pkl")

if __name__ == "__main__":
    train_and_save_model()
