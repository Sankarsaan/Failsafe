import sys
import os
import pandas as pd
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from database import SessionLocal, engine
import models
from ml_inference import process_csv
from auth import get_password_hash

def run_test():
    print("Resetting database...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Creating test user (CSE department)...")
    hashed_pw = get_password_hash("password")
    test_user = models.User(
        name="Test Faculty",
        email="faculty@test.com",
        hashed_password=hashed_pw,
        department=models.DepartmentEnum.cse,
        role=models.RoleEnum.faculty,
        status=models.StatusEnum.approved
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print("Generating valid CSV data for CSE (cs101, cs102)...")
    data = []
    for i in range(10):
        data.append({
            "id": f"STU-{i:03d}",
            "name": f"Student {i}",
            "roll_number": f"CSE-{i:03d}",
            "course_id": "cs101" if i < 5 else "cs102",
            "famsup": "no", "higher": "yes", "internet": "yes", "address": "U",
            "activities": "yes", "romantic": "no", "sup_paid": "no_no",
            "absentness": random.randint(0, 10), "past_failures": 0, "study_time": 2,
            "health": 3, "Pjob": 1, "Pedu": 2, "famrel": 3, "Alc": 2, "unstructured_time": 4
        })
    df = pd.DataFrame(data)
    df.to_csv("test_cse_students.csv", index=False)
    
    print("Processing CSV...")
    try:
        process_csv("test_cse_students.csv", db, test_user)
        print("Success! Data parsed and mapped to courses.")
    except Exception as e:
        print(f"Failed processing: {e}")
        
    print("Validating database state...")
    courses = db.query(models.Course).all()
    print(f"Courses created: {[c.course_id for c in courses]}")
    takes = db.query(models.Takes).all()
    print(f"Takes relationships created: {len(takes)}")
    students = db.query(models.Student).all()
    print(f"Students inserted: {len(students)}")
    
    print("Generating INVALID CSV data for CSE (me201)...")
    df['course_id'] = "me201"
    df.to_csv("test_invalid_students.csv", index=False)
    
    try:
        process_csv("test_invalid_students.csv", db, test_user)
        print("FAIL! It should have thrown an error.")
    except ValueError as e:
        print(f"Success! Correctly caught invalid course: {e}")
        
    db.close()

if __name__ == "__main__":
    run_test()
