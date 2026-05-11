import database
from sqlalchemy import text

db = database.SessionLocal()
db.execute(text("UPDATE students SET major = 'cse'"))
db.commit()
print("Updated existing students major to cse.")
