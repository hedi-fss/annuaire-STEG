import sqlite3
con = sqlite3.connect("instance/users_data.db")
cur=con.cursor()
cur.execute("Select* from user")
rows=cur.fetchall()
con.close()
for row in rows:
    print(row, '\n')
