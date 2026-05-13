# FAILSAFE — Faculty AI-powered Learning Safety & Early-warning System

> An intelligent early-warning platform that helps faculty identify at-risk students using Machine Learning (XGBoost + SHAP explainability), enabling timely, targeted interventions.

---

## 📑 Table of Contents
1. [System Overview](#system-overview)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [MySQL Database Setup](#mysql-database-setup)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Running the Application](#running-the-application)
8. [How the ML Model Works](#how-the-ml-model-works)
9. [Faculty Usage Guide](#faculty-usage-guide)
10. [CSV Upload Guide — Attribute Reference](#csv-upload-guide--attribute-reference)
11. [Faculty ID & Course Reference](#faculty-id--course-reference)

---

## System Overview

FAILSAFE follows a **role-based workflow**:

```
Institute Admin  →  Pre-populates the Course Table (with instructor names & faculty IDs)
Faculty          →  Registers using their Name + Faculty ID (verified against course table)
HOD              →  Reviews & Approves the faculty (courses are auto-linked upon approval)
Faculty          →  Uploads student CSVs for their assigned courses
System           →  Runs ML predictions + SHAP explanations
Faculty          →  Views Student Dashboard, Risk Levels, and Intervention Plans
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python), SQLAlchemy ORM |
| Database | MySQL (via PyMySQL) |
| ML Model | XGBoost Classifier + SHAP Explainability |
| Auth | JWT (python-jose), bcrypt password hashing |

---

## Prerequisites

Make sure you have these installed before proceeding:

- **Python 3.10+** — [python.org](https://python.org)
- **Node.js 18+** and **npm** — [nodejs.org](https://nodejs.org)
- **MySQL Server 8.0+** — [dev.mysql.com](https://dev.mysql.com/downloads/)
- **Git** — [git-scm.com](https://git-scm.com)

---

## MySQL Database Setup

### Step 1 — Start MySQL Server
Make sure your MySQL server is running on `localhost:3306`.

### Step 2 — Create the database
Open MySQL Workbench or any MySQL client and run:
```sql
CREATE DATABASE failsafe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 3 — Configure your connection
Open `backend/database.py` and update the connection string:

```python
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://<USERNAME>:<PASSWORD>@localhost:3306/failsafe"
)
```

Replace `<USERNAME>` and `<PASSWORD>` with your MySQL credentials.

> **Example** — for root user with password `mypassword`:
> ```python
> "mysql+pymysql://root:mypassword@localhost:3306/failsafe"
> ```
> If your password contains special characters (e.g. `@`, `#`), URL-encode them:
> - `@` → `%40`
> - `#` → `%23`
> - `$` → `%24`

Alternatively, set the `DATABASE_URL` environment variable in your shell:
```bash
# Windows PowerShell
$env:DATABASE_URL = "mysql+pymysql://root:mypassword@localhost:3306/failsafe"

# Linux / macOS
export DATABASE_URL="mysql+pymysql://root:mypassword@localhost:3306/failsafe"
```

---

## Backend Setup

### Step 1 — Navigate to the backend directory
```bash
cd backend
```

### Step 2 — Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run database migrations
This adds all required columns to existing tables:
```bash
python migrate_db.py
```

### Step 5 — Seed the HOD accounts
This creates one HOD admin account per department:
```bash
python seed_db.py
```
Default HOD credentials for each department:
| Department | Email | Password |
|---|---|---|
| CSE | `hod.cse@university.edu` | `password123` |
| MNC | `hod.mnc@university.edu` | `password123` |
| DSAI | `hod.dsai@university.edu` | `password123` |
| Electrical | `hod.electrical@university.edu` | `password123` |
| Mechanical | `hod.mechanical@university.edu` | `password123` |
| Chemical | `hod.chemical@university.edu` | `password123` |
| Civil | `hod.civil@university.edu` | `password123` |

> ⚠️ **Change default passwords** before any production use.

### Step 6 — Seed the Course Table
Populates 56 courses across all departments with instructor names and faculty IDs:
```bash
python seed_courses.py
```

### Step 7 — Train the ML Model (first time only)
```bash
python train_model.py
```
This downloads the UCI Student Performance dataset, trains the XGBoost model, and saves it as `por_student_model.pkl`.

> **Note:** This only needs to be run once. Pre-trained model files (`*.pkl`) are included if already generated.

---

## Frontend Setup

### Step 1 — Navigate to the project root
```bash
cd ..   # from backend/ back to project root
```

### Step 2 — Install Node dependencies
```bash
npm install
```

---

## Running the Application

Open **two separate terminal windows**:

### Terminal 1 — Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend runs at: **http://127.0.0.1:8000**
API documentation: **http://127.0.0.1:8000/docs**

### Terminal 2 — Frontend
```bash
npm run dev
```
Frontend runs at: **http://localhost:3000**

---

## How the ML Model Works

### Training Data
The model was trained on the **UCI Machine Learning Repository — Student Performance Dataset** (Portuguese language course, 649 students). Features were engineered from raw columns to create meaningful combined attributes.

### Algorithm
**XGBoost Classifier** in a scikit-learn Pipeline with:
- OneHotEncoding for categorical features
- RandomizedSearchCV for hyperparameter tuning (20 iterations, 3-fold CV)
- Balanced class weights to handle imbalanced risk distribution

### Risk Prediction
The final grade (G3) determines the target class:

| Grade (G3) | Risk Category | Code |
|---|---|---|
| G3 < 10 | **High Risk** | 2 |
| 10 ≤ G3 < 14 | **Moderate Risk** | 1 |
| G3 ≥ 14 | **Low Risk** | 0 |

> **Lowered Threshold:** A student is flagged **High Risk** if the model's confidence is > 25% (instead of the default 50%). This makes FAILSAFE more sensitive — it would rather flag a safe student than miss a truly at-risk one.

### SHAP Explainability
After predicting, **SHAP (SHapley Additive exPlanations)** values are computed per student. SHAP answers: *"Which attributes pushed THIS student's risk score up?"*

- **Positive SHAP value** → attribute increased the risk
- **Negative SHAP value** → attribute decreased the risk

The **Intervention Plan** card on each student's detail page shows the **Top 3 attributes with the highest positive SHAP impact**, mapped to actionable faculty recommendations.

---

## Faculty Usage Guide

### Step 1 — Register
1. Go to `http://localhost:3000/register`
2. Fill in your **Full Name** (must exactly match what is in the course table)
3. Enter your **Faculty ID** (e.g. `FAC-CSE-001` — provided by your institute)
4. Enter your email, password, and department
5. Submit — your account is sent for HOD approval

> ❗ Your name and Faculty ID **must match** what the institute entered in the course table. Registration will fail otherwise.

### Step 2 — Login
1. Go to `http://localhost:3000/login`
2. Enter your email, Faculty ID, and password
3. HODs can leave Faculty ID blank

### Step 3 — Wait for HOD Approval
Your account starts as **Pending**. The HOD for your department must approve you. Upon approval, your courses are automatically linked to your account.

### Step 4 — Upload Student Data
1. Go to **Upload Data** from the sidebar
2. Prepare your CSV file (see format guide below)
3. Drag & drop or click to select the file
4. Click **Upload and Process**
5. The ML model runs predictions automatically

### Step 5 — View Student Dashboard
- Go to **Students** in the sidebar
- Use the **course dropdown** (top right) to filter students by course
- Use the **search bar** to find students by name or ID

### Step 6 — View Individual Student Details
- Click **View Details** on any student
- See the **SHAP Bar Chart** — which attributes affect their risk the most
- See the **Intervention Plan** — Top 3 actionable priorities ranked by severity

---

## CSV Upload Guide — Attribute Reference

Your CSV file must have exactly these columns. Each row is one student.

### Required Identity Columns

| Column | Description | Example |
|---|---|---|
| `id` | Unique student ID | `STU-CS201-001` |
| `name` | Student's full name | `Aarav Sharma` |
| `roll_number` | Roll / registration number | `22CS001` |
| `course_id` | Course code (your assigned course) | `CS201` |

---

### 🔢 Numeric Attributes — Observe & Fill

| Column | What to Observe | Scale | Details |
|---|---|---|---|
| `absentness` | Total classes missed | **0 – 25** | Count from attendance register |
| `past_failures` | Number of prior course/year failures | **0, 1, 2, 3** | 3 means "3 or more" |
| `study_time` | Weekly study hours (outside class) | **1, 2, 3, 4** | 1 = < 2 hrs · 2 = 2–5 hrs · 3 = 5–10 hrs · 4 = > 10 hrs |
| `health` | Student's health status | **1 – 5** | 1 = very poor · 5 = excellent |
| `famrel` | Quality of student's family relationships | **1 – 5** | 1 = very bad · 5 = excellent |
| `Alc` | Alcohol consumption (weekday + weekend) | **2 – 10** | Sum of: weekday alcohol (1–5) + weekend alcohol (1–5) |
| `unstructured_time` | Free time + time going out combined | **2 – 10** | Sum of: free time (1–5) + going out (1–5) |
| `Pjob` | Parents' occupation level (both combined) | **0 – 6** | Per parent: at_home = 0, services/health/other = 1, teacher = 2. Add both parents. |
| `Pedu` | Parents' education level (both combined) | **0 – 8** | Per parent: 0 = none, 1 = primary, 2 = middle, 3 = secondary, 4 = higher. Add both parents. |

---

### 🔤 Categorical Attributes — Write Exactly as Shown

| Column | What to Observe | Allowed Values |
|---|---|---|
| `famsup` | Does the family provide academic support at home? | `yes` or `no` |
| `higher` | Does the student want to pursue higher education? | `yes` or `no` |
| `internet` | Does the student have internet access at home? | `yes` or `no` |
| `address` | Is the student's home in an urban or rural area? | `U` (urban) or `R` (rural) |
| `activities` | Does the student participate in extracurricular activities? | `yes` or `no` |
| `romantic` | Is the student in a romantic relationship? | `yes` or `no` |
| `sup_paid` | School support + paid tutoring (format: `schoolsup_paid`) | `yes_yes` · `yes_no` · `no_yes` · `no_no` |

**`sup_paid` explained:**
- `yes_yes` → Has school support AND paid private tutoring
- `yes_no` → Has school support but NO paid tutoring
- `no_yes` → No school support but HAS paid tutoring
- `no_no` → Has neither school support nor paid tutoring

---

### 📄 Sample CSV Row

```
id,name,roll_number,course_id,famsup,higher,internet,address,activities,romantic,sup_paid,absentness,past_failures,study_time,health,Pjob,Pedu,famrel,Alc,unstructured_time
STU-CS201-001,Aarav Sharma,22CS001,CS201,yes,yes,yes,U,yes,no,yes_no,4,0,3,4,3,4,4,1,3
STU-CS201-002,Priya Mehta,22CS002,CS201,no,yes,yes,U,no,no,no_no,14,2,1,2,1,2,2,4,5
```

A ready-to-use sample CSV for testing is available at:
`backend/student_data/cs201_sample.csv`

---

### ⚡ Quick Reference Card

```
NUMERIC:
  absentness         : Missed classes          → 0–25
  past_failures      : Prior failures          → 0, 1, 2, 3
  study_time         : Weekly study hrs        → 1(<2h) 2(2-5h) 3(5-10h) 4(>10h)
  health             : Health rating           → 1(bad) – 5(excellent)
  famrel             : Family relations        → 1(bad) – 5(excellent)
  Alc                : Weekday+Weekend alcohol → 2–10  (sum of two 1-5 scales)
  unstructured_time  : Freetime + Going out    → 2–10  (sum of two 1-5 scales)
  Pjob               : Both parents' job level → 0–6   (at_home=0 other=1 teacher=2, add both)
  Pedu               : Both parents' education → 0–8   (none=0 to higher=4, add both)

CATEGORICAL:
  famsup      → yes / no
  higher      → yes / no
  internet    → yes / no
  address     → U (urban) / R (rural)
  activities  → yes / no
  romantic    → yes / no
  sup_paid    → yes_yes / yes_no / no_yes / no_no
```

---

## Faculty ID & Course Reference

Faculty must use their **Faculty ID** when registering and logging in. Contact your institute admin for your Faculty ID. Below is the pre-populated course structure:

| Faculty ID | Instructor | Dept | Courses |
|---|---|---|---|
| FAC-CSE-001 | Dr. Arun Kumar | CSE | CS101, CS201 |
| FAC-CSE-002 | Dr. Priya Nair | CSE | CS102, CS202 |
| FAC-CSE-003 | Dr. Ravi Shankar | CSE | CS301, CS302 |
| FAC-CSE-004 | Dr. Suman Ghosh | CSE | CS401, CS402 |
| FAC-CSE-005 | Dr. Meena Pillai | CSE | CS403, CS404 |
| FAC-MNC-001 | Dr. Vivek Tripathi | MNC | MA101, MA102 |
| FAC-MNC-002 | Dr. Anjali Verma | MNC | MA201, MA202 |
| FAC-MNC-003 | Dr. Rajeev Bose | MNC | MA301, MA302 |
| FAC-MNC-004 | Dr. Suresh Iyer | MNC | MA401, MA402 |
| FAC-DSAI-001 | Dr. Kavya Menon | DSAI | DA101, DA102 |
| FAC-DSAI-002 | Dr. Arjun Reddy | DSAI | DA201, DA202 |
| FAC-DSAI-003 | Dr. Nisha Sharma | DSAI | DA301, DA302 |
| FAC-DSAI-004 | Dr. Hari Prasad | DSAI | DA401, DA402 |
| FAC-EE-001 | Dr. Balaji Rao | Electrical | EE101, EE102 |
| FAC-EE-002 | Dr. Sunita Kulkarni | Electrical | EE201, EE202 |
| FAC-EE-003 | Dr. Prakash Joshi | Electrical | EE301, EE302 |
| FAC-EE-004 | Dr. Rekha Nambiar | Electrical | EE401, EE402 |
| FAC-ME-001 | Dr. Subramaniam Pillai | Mechanical | ME101, ME102 |
| FAC-ME-002 | Dr. Geeta Malhotra | Mechanical | ME201, ME202 |
| FAC-ME-003 | Dr. Krishnan Nair | Mechanical | ME301, ME302 |
| FAC-ME-004 | Dr. Pavan Desai | Mechanical | ME401, ME402 |
| FAC-CHE-001 | Dr. Anand Murthy | Chemical | CE101, CE102 |
| FAC-CHE-002 | Dr. Usha Rani | Chemical | CE201, CE202 |
| FAC-CHE-003 | Dr. Naveen Kumar | Chemical | CE301, CE302 |
| FAC-CHE-004 | Dr. Deepa Srinivasan | Chemical | CE401, CE402 |
| FAC-CIV-001 | Dr. Mohan Lal | Civil | CL101, CL102 |
| FAC-CIV-002 | Dr. Seema Agarwal | Civil | CL201, CL202 |
| FAC-CIV-003 | Dr. Vinod Pandey | Civil | CL301, CL302 |
| FAC-CIV-004 | Dr. Sudha Krishnaswamy | Civil | CL401, CL402 |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `Unknown column 'faculty_id_str'` error | Run `python migrate_db.py` in the backend folder |
| `Connection refused` on backend | Make sure `uvicorn main:app --reload` is running |
| `Another next dev server is already running` | Run `taskkill /F /IM node.exe /T` then restart `npm run dev` |
| Course not found during upload | Ensure course ID matches exactly what's in the course table (case-insensitive) |
| Registration rejected | Name and Faculty ID must **exactly match** what's in the course table |
| HOD can't see pending faculty | HOD can only see faculty from their own department |

---

*FAILSAFE — Built for proactive student support through responsible AI.*
