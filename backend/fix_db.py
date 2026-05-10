import database
from sqlalchemy import text

db = database.SessionLocal()
db.execute(text("DELETE FROM users WHERE department NOT IN ('cse', 'mnc', 'dsai', 'mechanical', 'chemical', 'civil', 'electrical')"))
db.commit()
print("Fixed DB")
