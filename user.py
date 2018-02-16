import uuid
import sqlite3

conn=sqlite3.connect('/Users/jgoldader/lbypl.db')
c=conn.cursor()

c.execute("SELECT * FROM providers")
print(c.fetchall())

user_id=uuid.uuid4()
print(user_id)