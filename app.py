from flask import Flask, render_template, request, redirect, url_for
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
    return redirect(url_for('show_form'))

@app.route("/form")
def show_form():
    Program = [
        "Computer Science",
        "Artificial Intelligence",
        "Software Engineering",
        "CyberSecurity",
        "Mechanical Engineering",
        "Electrical Engineering",
        "Civil Engineering", 
        "Computer Engineering",
        "Engineering Sciences",
        "Material Science & Chemical Engineering",
        "School of Management Sciences"
        ]
    Semester = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th" , "8th"]
    
    Department = ["FCSE", "FES", "FEE", "FME", "MGS", "FMCE"]
    
    Month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    Year = list(range(1980, 2025))
    
    return render_template("form.html", Semester=Semester, Program=Program, Department=Department, Month=Month, Year=Year)

@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == "__main__":
    app.run(debug=True)