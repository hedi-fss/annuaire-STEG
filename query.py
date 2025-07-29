import sqlite3
con = sqlite3.connect("instance/users_data.db")
cur=con.cursor()
cur.execute("Update service set nom='Secrétariat' where Id_service=10")
con.commit()
con.close()