import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import train_test_split
print("Loading data...")
df = pd.read_csv("/home/jarvis/student_data/student-por.csv", sep=";")
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
print("Loading model...")
pipeline = joblib.load("/home/jarvis/student_model.pkl")
print("Generating predictions...")
y_probs = pipeline.predict_proba(X_test)
# We want the Precision-Recall curve for "High Risk" (Class 2)
y_test_binary = (y_test == 2).astype(int)
y_scores_high_risk = y_probs[:, 2]
precision, recall, thresholds = precision_recall_curve(y_test_binary, y_scores_high_risk)
plt.figure(figsize=(10, 6))
plt.plot(thresholds, precision[:-1], "b--", label="Precision", linewidth=2)
plt.plot(thresholds, recall[:-1], "g-", label="Recall", linewidth=2)
plt.xlabel("Threshold (Probability of High Risk)", fontsize=12)
plt.ylabel("Score", fontsize=12)
plt.title("Precision-Recall Tradeoff for High Risk Students", fontsize=14)
plt.legend(loc="best", fontsize=12)
plt.grid(True)
plt.xlim([0, 1])
plt.ylim([0, 1.05])
# Find the intersection point
intersection_idx = np.argmin(np.abs(precision[:-1] - recall[:-1]))
best_thresh = thresholds[intersection_idx]
best_score = precision[intersection_idx]
plt.plot(best_thresh, best_score, 'ro', markersize=8)
plt.annotate(f'Intersection\nThr={best_thresh:.2f}', 
             xy=(best_thresh, best_score), 
             xytext=(best_thresh + 0.05, best_score + 0.1),
             arrowprops=dict(facecolor='red', shrink=0.05))
# Also mark our chosen 0.25 threshold
chosen_idx = np.argmin(np.abs(thresholds - 0.25))
plt.plot(0.25, precision[chosen_idx], 'bo', markersize=6)
plt.plot(0.25, recall[chosen_idx], 'go', markersize=6)
plt.axvline(x=0.25, color='gray', linestyle=':', label='Chosen 0.25 Threshold')
plt.legend(loc="best")
save_path = "/home/jarvis/por_pr_curve.png"
plt.savefig(save_path, bbox_inches='tight')
print(f"Plot saved to {save_path}")