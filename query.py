import sqlite3
con = sqlite3.connect("instance/users_data.db")
cur=con.cursor()
cur.execute("Update service set nom='Intelligence Artificielle' where nom='IA'")
con.commit()
con.close()