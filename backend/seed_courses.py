import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
import models
from models import Course, DepartmentEnum

# All courses across departments with unique IDs, instructor names, and faculty IDs
COURSES = [
    # --- CSE ---
    ("CS101", "Introduction to Programming", "Dr. Arun Kumar", "FAC-CSE-001", "cse"),
    ("CS102", "Data Structures", "Dr. Priya Nair", "FAC-CSE-002", "cse"),
    ("CS201", "Algorithms & Complexity", "Dr. Arun Kumar", "FAC-CSE-001", "cse"),
    ("CS202", "Database Management Systems", "Dr. Priya Nair", "FAC-CSE-002", "cse"),
    ("CS301", "Computer Networks", "Dr. Ravi Shankar", "FAC-CSE-003", "cse"),
    ("CS302", "Operating Systems", "Dr. Ravi Shankar", "FAC-CSE-003", "cse"),
    ("CS401", "Machine Learning", "Dr. Suman Ghosh", "FAC-CSE-004", "cse"),
    ("CS402", "Software Engineering", "Dr. Suman Ghosh", "FAC-CSE-004", "cse"),
    ("CS403", "Cloud Computing", "Dr. Meena Pillai", "FAC-CSE-005", "cse"),
    ("CS404", "Cybersecurity Fundamentals", "Dr. Meena Pillai", "FAC-CSE-005", "cse"),

    # --- MNC ---
    ("MA101", "Calculus & Analysis", "Dr. Vivek Tripathi", "FAC-MNC-001", "mnc"),
    ("MA102", "Linear Algebra", "Dr. Vivek Tripathi", "FAC-MNC-001", "mnc"),
    ("MA201", "Probability & Statistics", "Dr. Anjali Verma", "FAC-MNC-002", "mnc"),
    ("MA202", "Numerical Methods", "Dr. Anjali Verma", "FAC-MNC-002", "mnc"),
    ("MA301", "Discrete Mathematics", "Dr. Rajeev Bose", "FAC-MNC-003", "mnc"),
    ("MA302", "Graph Theory", "Dr. Rajeev Bose", "FAC-MNC-003", "mnc"),
    ("MA401", "Cryptography", "Dr. Suresh Iyer", "FAC-MNC-004", "mnc"),
    ("MA402", "Operations Research", "Dr. Suresh Iyer", "FAC-MNC-004", "mnc"),

    # --- DSAI ---
    ("DA101", "Python for Data Science", "Dr. Kavya Menon", "FAC-DSAI-001", "dsai"),
    ("DA102", "Statistical Learning", "Dr. Kavya Menon", "FAC-DSAI-001", "dsai"),
    ("DA201", "Deep Learning", "Dr. Arjun Reddy", "FAC-DSAI-002", "dsai"),
    ("DA202", "Natural Language Processing", "Dr. Arjun Reddy", "FAC-DSAI-002", "dsai"),
    ("DA301", "Big Data Analytics", "Dr. Nisha Sharma", "FAC-DSAI-003", "dsai"),
    ("DA302", "Computer Vision", "Dr. Nisha Sharma", "FAC-DSAI-003", "dsai"),
    ("DA401", "Reinforcement Learning", "Dr. Hari Prasad", "FAC-DSAI-004", "dsai"),
    ("DA402", "AI Ethics & Governance", "Dr. Hari Prasad", "FAC-DSAI-004", "dsai"),

    # --- Electrical ---
    ("EE101", "Circuit Theory", "Dr. Balaji Rao", "FAC-EE-001", "electrical"),
    ("EE102", "Signals & Systems", "Dr. Balaji Rao", "FAC-EE-001", "electrical"),
    ("EE201", "Electromagnetic Fields", "Dr. Sunita Kulkarni", "FAC-EE-002", "electrical"),
    ("EE202", "Power Systems", "Dr. Sunita Kulkarni", "FAC-EE-002", "electrical"),
    ("EE301", "Control Systems", "Dr. Prakash Joshi", "FAC-EE-003", "electrical"),
    ("EE302", "Digital Electronics", "Dr. Prakash Joshi", "FAC-EE-003", "electrical"),
    ("EE401", "VLSI Design", "Dr. Rekha Nambiar", "FAC-EE-004", "electrical"),
    ("EE402", "Embedded Systems", "Dr. Rekha Nambiar", "FAC-EE-004", "electrical"),

    # --- Mechanical ---
    ("ME101", "Engineering Mechanics", "Dr. Subramaniam Pillai", "FAC-ME-001", "mechanical"),
    ("ME102", "Thermodynamics", "Dr. Subramaniam Pillai", "FAC-ME-001", "mechanical"),
    ("ME201", "Fluid Mechanics", "Dr. Geeta Malhotra", "FAC-ME-002", "mechanical"),
    ("ME202", "Manufacturing Processes", "Dr. Geeta Malhotra", "FAC-ME-002", "mechanical"),
    ("ME301", "Machine Design", "Dr. Krishnan Nair", "FAC-ME-003", "mechanical"),
    ("ME302", "Heat Transfer", "Dr. Krishnan Nair", "FAC-ME-003", "mechanical"),
    ("ME401", "Robotics & Automation", "Dr. Pavan Desai", "FAC-ME-004", "mechanical"),
    ("ME402", "Industrial Engineering", "Dr. Pavan Desai", "FAC-ME-004", "mechanical"),

    # --- Chemical ---
    ("CE101", "Chemical Engineering Principles", "Dr. Anand Murthy", "FAC-CHE-001", "chemical"),
    ("CE102", "Mass & Energy Balances", "Dr. Anand Murthy", "FAC-CHE-001", "chemical"),
    ("CE201", "Transport Phenomena", "Dr. Usha Rani", "FAC-CHE-002", "chemical"),
    ("CE202", "Reaction Engineering", "Dr. Usha Rani", "FAC-CHE-002", "chemical"),
    ("CE301", "Process Control", "Dr. Naveen Kumar", "FAC-CHE-003", "chemical"),
    ("CE302", "Separation Processes", "Dr. Naveen Kumar", "FAC-CHE-003", "chemical"),
    ("CE401", "Biochemical Engineering", "Dr. Deepa Srinivasan", "FAC-CHE-004", "chemical"),
    ("CE402", "Environmental Engineering", "Dr. Deepa Srinivasan", "FAC-CHE-004", "chemical"),

    # --- Civil ---
    ("CL101", "Engineering Drawing", "Dr. Mohan Lal", "FAC-CIV-001", "civil"),
    ("CL102", "Strength of Materials", "Dr. Mohan Lal", "FAC-CIV-001", "civil"),
    ("CL201", "Structural Analysis", "Dr. Seema Agarwal", "FAC-CIV-002", "civil"),
    ("CL202", "Soil Mechanics", "Dr. Seema Agarwal", "FAC-CIV-002", "civil"),
    ("CL301", "Concrete Technology", "Dr. Vinod Pandey", "FAC-CIV-003", "civil"),
    ("CL302", "Transportation Engineering", "Dr. Vinod Pandey", "FAC-CIV-003", "civil"),
    ("CL401", "Water Resources Engineering", "Dr. Sudha Krishnaswamy", "FAC-CIV-004", "civil"),
    ("CL402", "Construction Management", "Dr. Sudha Krishnaswamy", "FAC-CIV-004", "civil"),
]

def seed_courses():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    added = 0
    skipped = 0
    for course_id, course_name, instructor_name, instructor_faculty_id, dept in COURSES:
        existing = db.query(Course).filter(Course.course_id == course_id).first()
        if not existing:
            course = Course(
                course_id=course_id,
                course_name=course_name,
                instructor_name=instructor_name,
                instructor_faculty_id=instructor_faculty_id,
                faculty_id=None  # Will be assigned when faculty registers & gets approved
            )
            db.add(course)
            added += 1
        else:
            # Update instructor info if missing
            if not existing.instructor_name:
                existing.instructor_name = instructor_name
            if not existing.instructor_faculty_id:
                existing.instructor_faculty_id = instructor_faculty_id
            skipped += 1

    db.commit()
    db.close()
    print(f"Course seeding complete. Added: {added}, Skipped (already exist): {skipped}")
    print("\n--- Course Table Summary ---")
    db2 = SessionLocal()
    all_courses = db2.query(Course).all()
    for c in all_courses:
        print(f"  [{c.course_id}] {c.course_name} | Instructor: {c.instructor_name} | FacultyID: {c.instructor_faculty_id}")
    db2.close()

if __name__ == "__main__":
    seed_courses()
