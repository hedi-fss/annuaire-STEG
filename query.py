import pandas as pd
import sqlite3
con = sqlite3.connect("instance/users_data.db")
df = pd.read_sql("SELECT * from service", con)
print(df)