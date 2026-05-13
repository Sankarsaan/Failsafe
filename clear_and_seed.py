import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from database import SessionLocal
from ml_inference import process_csv
import models

def clear_and_seed():
    print("Clearing old student data...")
    db = SessionLocal()
    try:
        # Delete old records
        db.query(models.RiskPrediction).delete()
        db.query(models.PerformanceRecord).delete()
        db.query(models.Student).delete()
        db.commit()
        print("Old student data cleared.")
        
        print("Seeding new student data from large_sample_students.csv...")
        process_csv("large_sample_students.csv", db)
        print("Seeding complete! Database has a new distribution of students.")
    except Exception as e:
        print(f"Error during clearing and seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_and_seed()
