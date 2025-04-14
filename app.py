from flask import Flask, render_template, request, redirect
import psycopg2
from datetime import date

app = Flask(__name__)

@app.route("/")
def signup():
    return render_template("signup.html")

#connecting flask with database using psycopg2
def get_db_connection():
    conn = psycopg2.connect(
        dbname="Students_db",
        user="postgres",
        password="abc123",
        host="localhost",
        port="5432"
    )
    return conn

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    today = date.today()
    user_id = hash(email) % 100000
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Students (id, name, email, password, registeration_date) VALUES (%s, %s, %s, %s, %s)",
        (user_id, name, email, password, today)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == "__main__":
    app.run(debug=True)