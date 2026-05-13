import sys
import os

# Add current dir to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
import models
from models import User, RoleEnum, StatusEnum, DepartmentEnum
from auth import get_password_hash
from sqlalchemy import text

def seed():
    # Attempt to add columns if they don't exist (MySQL/SQLite rough handling)
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(255) DEFAULT 'faculty'"))
            conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(255) DEFAULT 'pending'"))
    except Exception as e:
        print("Columns might already exist or DB doesn't support this ALTER:", e)
    
    # Also attempt to alter department in users if it's not the right type
    try:
        with engine.begin() as conn:
            # We don't drop the table, but if needed we could. 
            pass
    except Exception as e:
        pass

    # Recreate tables to be safe for any new ones
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    departments = [
        DepartmentEnum.cse,
        DepartmentEnum.mnc,
        DepartmentEnum.dsai,
        DepartmentEnum.mechanical,
        DepartmentEnum.chemical,
        DepartmentEnum.civil,
        DepartmentEnum.electrical
    ]

    for dept in departments:
        email = f"hod_{dept.value}@failsafe.edu"
        existing_hod = db.query(User).filter(User.email == email).first()
        
        if not existing_hod:
            print(f"Creating HOD for {dept.value}...")
            new_hod = User(
                name=f"HOD {dept.value.upper()}",
                email=email,
                hashed_password=get_password_hash("password123"), # Default password
                department=dept,
                role=RoleEnum.admin,
                status=StatusEnum.approved
            )
            db.add(new_hod)
        else:
            print(f"HOD for {dept.value} already exists.")
            # Ensure it has correct role and status
            existing_hod.role = RoleEnum.admin
            existing_hod.status = StatusEnum.approved
            existing_hod.department = dept
    
    db.commit()
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
