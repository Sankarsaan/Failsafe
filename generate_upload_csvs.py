import pandas as pd
import random
import uuid

def generate_csv(filename, course_ids, prefix=""):
    data = []
    
    for _ in range(15):  # 15 students per file
        cid = random.choice(course_ids)
        # Randomize risk features
        risk_level = random.choice(["high", "low", "moderate"])
        
        if risk_level == "high":
            absentness = random.randint(15, 30)
            failures = random.randint(2, 3)
            study = random.randint(1, 2)
            health = random.randint(1, 3)
        elif risk_level == "low":
            absentness = random.randint(0, 2)
            failures = 0
            study = random.randint(3, 4)
            health = random.randint(4, 5)
        else:
            absentness = random.randint(4, 10)
            failures = random.randint(0, 1)
            study = random.randint(2, 3)
            health = random.randint(3, 4)

        data.append({
            "id": f"STU-{uuid.uuid4().hex[:6].upper()}",
            "name": f"Test Student {random.randint(100, 999)}",
            "roll_number": f"{prefix}{random.randint(1000, 9999)}",
            "course_id": cid,
            "famsup": random.choice(["yes", "no"]),
            "higher": random.choice(["yes", "no"]),
            "internet": random.choice(["yes", "no"]),
            "address": random.choice(["U", "R"]),
            "activities": random.choice(["yes", "no"]),
            "romantic": random.choice(["yes", "no"]),
            "sup_paid": random.choice(["yes_yes", "no_no", "yes_no", "no_yes"]),
            "absentness": absentness,
            "past_failures": failures,
            "study_time": study,
            "health": health,
            "Pjob": random.randint(0, 4),
            "Pedu": random.randint(0, 4),
            "famrel": random.randint(1, 5),
            "Alc": random.randint(1, 5),
            "unstructured_time": random.randint(1, 5)
        })
        
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Generated {filename} with {len(df)} records across courses: {course_ids}")

if __name__ == "__main__":
    generate_csv("sample_cse_upload.csv", ["cs101", "cs205", "cs301"], "CSE-")
    generate_csv("sample_mech_upload.csv", ["me101", "me405"], "MECH-")
    generate_csv("sample_ee_upload.csv", ["ee202", "ee305"], "EE-")
    print("All sample CSVs generated successfully!")
