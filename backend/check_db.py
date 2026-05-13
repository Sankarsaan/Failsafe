import sys
sys.path.append('.')
from database import engine
from sqlalchemy import inspect

insp = inspect(engine)

print("=== users columns ===")
for col in insp.get_columns('users'):
    print(f"  {col['name']} : {col['type']}")

print()
print("=== courses columns ===")
for col in insp.get_columns('courses'):
    print(f"  {col['name']} : {col['type']}")

print()
print("=== sample courses rows (instructor_faculty_id) ===")
from database import SessionLocal
from models import Course
db = SessionLocal()
for c in db.query(Course).limit(5).all():
    print(f"  [{c.course_id}] instructor_name={c.instructor_name!r}  instructor_faculty_id={c.instructor_faculty_id!r}  faculty_id={c.faculty_id!r}")
db.close()
