import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from database import SessionLocal
import models
from auth import get_password_hash

def seed_hods():
    db = SessionLocal()
    try:
        departments = [
            models.DepartmentEnum.cse,
            models.DepartmentEnum.mnc,
            models.DepartmentEnum.dsai,
            models.DepartmentEnum.mechanical,
            models.DepartmentEnum.chemical,
            models.DepartmentEnum.civil,
            models.DepartmentEnum.electrical
        ]

        # We will use the same password for all HODs for testing purposes
        raw_password = "password123"
        hashed_pw = get_password_hash(raw_password)

        credentials = []

        for dept in departments:
            email = f"hod_{dept.value}@failsafe.edu"
            
            # Check if User already exists
            user = db.query(models.User).filter(models.User.email == email).first()
            if not user:
                user = models.User(
                    name=f"HOD {dept.value.upper()}",
                    email=email,
                    hashed_password=hashed_pw,
                    department=dept,
                    role=models.RoleEnum.admin,
                    status=models.StatusEnum.approved
                )
                db.add(user)
            else:
                user.role = models.RoleEnum.admin
                user.status = models.StatusEnum.approved
                user.hashed_password = hashed_pw

            # Check if Hod table record exists (just in case)
            hod = db.query(models.Hod).filter(models.Hod.department == dept).first()
            if not hod:
                hod = models.Hod(
                    email=email,
                    hashed_password=hashed_pw,
                    department=dept
                )
                db.add(hod)
            else:
                hod.email = email
                hod.hashed_password = hashed_pw
            
            credentials.append({"dept": dept.value.upper(), "email": email, "password": raw_password})

        db.commit()
        print("Successfully seeded HODs into the database.")
        for cred in credentials:
            print(f"{cred['dept']}: {cred['email']} / {cred['password']}")

    except Exception as e:
        print(f"Error seeding HODs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_hods()
