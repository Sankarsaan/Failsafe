import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from database import get_db
from ml_inference import process_csv
from sqlalchemy.orm import Session
from database import SessionLocal

def test_inference():
    print("Testing ML inference process...")
    db = SessionLocal()
    try:
        process_csv("sample_students.csv", db)
        print("Inference completed successfully!")
    except Exception as e:
        print(f"Error during inference: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_inference()
