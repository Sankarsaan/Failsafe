# Failsafe - Educational Platform

Failsafe is a full-stack educational platform with a decentralized Role-Based Access Control (RBAC) system. The application consists of a **Next.js frontend** and a **FastAPI backend** connected to a MySQL database.

## Prerequisites

Before running the application, make sure you have the following installed:
- [Node.js](https://nodejs.org/) (v18 or newer)
- [Python](https://www.python.org/) (3.10 or newer)
- [MySQL](https://www.mysql.com/) server running locally

---

## 1. Setting up the Backend

The backend is built with FastAPI, SQLAlchemy, and MySQL. It manages the database, authentication, and machine learning inferences.

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

Ensure your MySQL server is running and the database specified in your `database.py` is created.

To initialize the database and create the default Head of Department (HOD) admin accounts:
```bash
python seed_db.py
```
*Note: The default password for seeded HOD accounts is `password123`.*

### Running the Backend

Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```
The backend API will be available at `http://127.0.0.1:8000`. You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

## 2. Setting up the Frontend

The frontend is a modern web application built with Next.js (App Router), Tailwind CSS, and Shadcn UI.

### Installation

1. Open a **new terminal window** and navigate to the project root directory (if not already there).

2. Install the Node.js dependencies:
   ```bash
   npm install
   ```

### Running the Frontend

Start the Next.js development server:
```bash
npm run dev
```
The frontend application will be available at `http://localhost:3000`.

---

## Role-Based Workflow

1. **HOD Admins:** Log in using the seeded HOD accounts (e.g., `hod.cse@university.edu` / `password123`) to access the Admin Dashboard.
2. **Faculty:** New faculty members can register an account, but must wait for approval. They will appear as "Pending" on the respective HOD's dashboard.
3. Once approved by the HOD, the faculty member can log in and access the primary student intervention dashboard.
