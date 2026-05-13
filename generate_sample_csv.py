import pandas as pd
import random

def generate_sample_students():
    names = ["Alice Johnson", "Bob Smith", "Charlie Davis", "Diana Evans", "Evan Wright", "Fiona Green"]
    majors = ["cse", "mnc", "dsai", "mechanical", "chemical", "civil", "electrical"]
    years = ["Freshman", "Sophomore", "Junior", "Senior"]

    data = []
    for i, name in enumerate(names):
        student_id = f"STU-{i+1:03d}"
        major = majors[i % len(majors)]
        year = random.choice(years)
        
        # Categorical features
        famsup = random.choice(['yes', 'no'])
        higher = random.choice(['yes', 'no'])
        internet = random.choice(['yes', 'no'])
        address = random.choice(['U', 'R'])
        activities = random.choice(['yes', 'no'])
        romantic = random.choice(['yes', 'no'])
        sup_paid = random.choice(['yes_yes', 'no_yes', 'yes_no', 'no_no'])
        
        # Numeric features
        absentness = random.randint(0, 20)
        past_failures = random.randint(0, 3)
        study_time = random.randint(1, 4)
        health = random.randint(1, 5)
        Pjob = random.randint(0, 4)
        Pedu = random.randint(0, 8)
        famrel = random.randint(1, 5)
        Alc = random.randint(2, 10)
        unstructured_time = random.randint(2, 10)
        
        row = {
            "id": student_id,
            "name": name,
            "major": major,
            "year": year,
            "famsup": famsup,
            "higher": higher,
            "internet": internet,
            "address": address,
            "activities": activities,
            "romantic": romantic,
            "sup_paid": sup_paid,
            "absentness": absentness,
            "past_failures": past_failures,
            "study_time": study_time,
            "health": health,
            "Pjob": Pjob,
            "Pedu": Pedu,
            "famrel": famrel,
            "Alc": Alc,
            "unstructured_time": unstructured_time
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv("sample_students.csv", index=False)
    print("Generated sample_students.csv with 6 records.")

if __name__ == "__main__":
    generate_sample_students()
