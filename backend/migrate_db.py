import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def migrate():
    with engine.begin() as conn:
        # Add faculty_id_str to users
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN faculty_id_str VARCHAR(255) NULL"))
            print("Added faculty_id_str to users")
        except Exception as e:
            print(f"faculty_id_str might already exist: {e}")

        # Add instructor_name to courses
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN instructor_name VARCHAR(255) NULL"))
            print("Added instructor_name to courses")
        except Exception as e:
            print(f"instructor_name might already exist: {e}")

        # Add instructor_faculty_id to courses
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN instructor_faculty_id VARCHAR(255) NULL"))
            print("Added instructor_faculty_id to courses")
        except Exception as e:
            print(f"instructor_faculty_id might already exist: {e}")

        # Make faculty_id nullable in courses
        try:
            conn.execute(text("ALTER TABLE courses MODIFY COLUMN faculty_id INT NULL"))
            print("Made faculty_id nullable in courses")
        except Exception as e:
            print(f"Could not modify faculty_id nullable: {e}")

    print("Migration complete.")

if __name__ == "__main__":
    migrate()
