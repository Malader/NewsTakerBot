import sqlite3

conn = sqlite3.connect('tgbotdatabase.sqlite')
cursor = conn.cursor()

cursor.execute("SELECT * FROM user_channels")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
