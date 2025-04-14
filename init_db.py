#this file is for me to set thing up while app.py is for the users to 
#interact with live app
import psycopg2

conn = psycopg2.connect(
    dbname = "Students_db",
    user="postgres",
    password="abc123",
    host="localhost",
    port="5432"
    )

cur = conn.cursor()
cur.execute("INSERT INTO Students(name) VALUES (%s)", ("Adan",))
conn.commit()
cur.close()
conn.close()