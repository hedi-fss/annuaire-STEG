import sqlite3
con = sqlite3.connect("instance/users_data.db")
cur=con.cursor()
cur.execute("Select matricule, nom, tel, acces from user order by matricule")
rows=cur.fetchall()
con.close()
for row in rows:
    print(row,'\n')