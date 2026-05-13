import pandas as pd
import random
import os

def generate_varied_students():
    majors = ["cse", "mnc", "dsai", "mechanical", "chemical", "civil", "electrical"]
    years = ["Freshman", "Sophomore", "Junior", "Senior"]

    data = []
    
    # Generate 20 High Risk
    for i in range(20):
        student_id = f"STU-H{i+1:03d}"
        data.append({
            "id": student_id,
            "name": f"HighRisk Student {i+1}",
            "major": random.choice(majors),
            "year": random.choice(years),
            "famsup": "no",
            "higher": "no",
            "internet": "no",
            "address": "R",
            "activities": "no",
            "romantic": "yes",
            "sup_paid": "no_no",
            "absentness": random.randint(15, 30),
            "past_failures": random.randint(2, 3),
            "study_time": random.randint(1, 2),
            "health": random.randint(1, 3),
            "Pjob": random.randint(0, 1),
            "Pedu": random.randint(0, 2),
            "famrel": random.randint(1, 2),
            "Alc": random.randint(6, 10),
            "unstructured_time": random.randint(6, 10)
        })

    # Generate 20 Moderate Risk
    for i in range(20):
        student_id = f"STU-M{i+1:03d}"
        data.append({
            "id": student_id,
            "name": f"ModerateRisk Student {i+1}",
            "major": random.choice(majors),
            "year": random.choice(years),
            "famsup": "yes",
            "higher": "yes",
            "internet": "yes",
            "address": "U",
            "activities": "yes",
            "romantic": "no",
            "sup_paid": "no_yes",
            "absentness": random.randint(4, 10),
            "past_failures": random.randint(0, 1),
            "study_time": random.randint(2, 3),
            "health": random.randint(3, 4),
            "Pjob": random.randint(2, 3),
            "Pedu": random.randint(3, 5),
            "famrel": random.randint(3, 4),
            "Alc": random.randint(3, 6),
            "unstructured_time": random.randint(4, 7)
        })

    # Generate 20 Low Risk
    for i in range(20):
        student_id = f"STU-L{i+1:03d}"
        data.append({
            "id": student_id,
            "name": f"LowRisk Student {i+1}",
            "major": random.choice(majors),
            "year": random.choice(years),
            "famsup": "yes",
            "higher": "yes",
            "internet": "yes",
            "address": "U",
            "activities": "yes",
            "romantic": "no",
            "sup_paid": "yes_yes",
            "absentness": random.randint(0, 2),
            "past_failures": 0,
            "study_time": random.randint(3, 4),
            "health": random.randint(4, 5),
            "Pjob": random.randint(3, 4),
            "Pedu": random.randint(6, 8),
            "famrel": random.randint(4, 5),
            "Alc": random.randint(2, 3),
            "unstructured_time": random.randint(2, 4)
        })
        
    random.shuffle(data)
    df = pd.DataFrame(data)
    df.to_csv("large_sample_students.csv", index=False)
    print("Generated large_sample_students.csv with 60 records.")

if __name__ == "__main__":
    generate_varied_students()
