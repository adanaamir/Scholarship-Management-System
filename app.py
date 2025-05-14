from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from datetime import datetime
import psycopg2.extras
from reportlab.pdfgen import canvas
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="Scholarship_Management",
        user="postgres",
        password="abc123",
        host="localhost",
        port="5432"
    )

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome Page</title>
        <style>
            body {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            h1 {
                font-size: 36px;
                margin-bottom: 40px;
                font-weight: 600;
            }
            .button-container {
                display: flex;
                flex-direction: column;
                gap: 15px;
                width: 300px;
            }
            a {
                text-decoration: none;
                color: #fff;
                background-color: #007bff;
                padding: 12px;
                border-radius: 5px;
                font-size: 18px;
                text-align: center;
                transition: background-color 0.3s ease;
            }
            a:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to the Scholarship Management System</h1>
        <div class="button-container">
            <a href="/login_student">Login as Student</a>
            <a href="/login_admin">Login as Admin</a>
            <a href="/register_student">Register as Student</a>
            <a href="/register_admin">Register as Admin</a>
            <a href="/admin_manage">Manage Admins (Admin Only)</a>
            <a href="/student_manage">Manage Students (Student Only)</a>
        </div>
    </body>
    </html>
    '''

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        student_name = request.form['name']
        email = request.form['email']
        student_pass = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO students (student_name, email, student_pass)
            VALUES (%s, %s, %s)
        ''', (student_name, email, student_pass))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login_student')  # You need to implement this route/view

    return render_template('register_student.html')

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO admins (name, email, password, created_at) VALUES (%s, %s, %s, %s)',
                    (name, email, password, datetime.now().date()))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login_admin')
    
    return render_template('register_admin.html')


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM students WHERE email=%s AND student_pass=%s', (email, password))
        student = cur.fetchone()
        cur.close()
        conn.close()

        if student:
            session['student_id'] = student[0]
            session['email'] = email
            session['user_type'] = 'student'
            return redirect('/student_dashboard')  # This should be a route you define for the dashboard
        else:
            return 'Invalid credentials! Try again.'

    return render_template('login_student.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM admins WHERE email=%s AND password=%s', (email, password))
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin:
            session['admin_id'] = admin[0]
            session['user_type'] = 'admin'
            return redirect('/admin_dashboard')
        else:
            return 'Invalid credentials! Try again.'
    
    return render_template('login_admin.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login_student'))

    conn = get_db_connection()
    cur = conn.cursor()
    student_id = session['student_id']

    #showing scholarships the student has NOT applied to
    cur.execute("""
        SELECT s.scholarship_id, s.title FROM scholarships s
        WHERE s.scholarship_id NOT IN (
            SELECT scholarship_id FROM scholarship_applications WHERE student_id = %s
        )
    """, (student_id,))
    scholarships = cur.fetchall()

    #showing all applications by the student with their current status and review letter
    cur.execute("""
        SELECT sa.application_id, sa.status, sa.review_letter, sa.application_date, sa.applied_on, sc.title
        FROM scholarship_applications sa
        JOIN scholarships sc ON sa.scholarship_id = sc.scholarship_id
        WHERE sa.student_id = %s
    """, (student_id,))
    applications = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'student_dashboard.html',
        scholarships=scholarships,
        applications=applications,
        email=session.get('email')
    )
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))
    return render_template('admin_dashboard.html')

@app.route('/admin/review', methods=['GET', 'POST'])
def admin_review():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        app_id = request.form['app_id']
        status = request.form['status']
        comment = request.form['comment']

        cur.execute("""
            UPDATE scholarship_applications
            SET status = %s, review_letter = %s
            WHERE application_id = %s
        """, (status, comment, app_id))
        conn.commit()

    # DO NOT insert a new application here
    # Just fetch pending or null-status applications
    cur.execute("""
      SELECT application_id, student_id, scholarship_id, status, review_letter, application_date, applied_on, application_pdf
      FROM scholarship_applications
      WHERE status IS NULL OR status = 'Pending'
""")

    scholarship_applications = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin_review.html', scholarship_applications=scholarship_applications)

@app.route('/create_form', methods=['GET', 'POST'])
def create_form():

    if request.method == 'POST':
        title = request.form['scholarship_title']
        description = request.form['scholarship_description']
        eligibility = request.form['scholarship_eligibility']
        questions = request.form.getlist('questions[]')
        question_types = request.form.getlist('question_types[]')

        conn = get_db_connection()
        cur = conn.cursor()

        # Insert into scholarships
        cur.execute("""
            INSERT INTO scholarships (title, description, eligibility)
            VALUES (%s, %s, %s) RETURNING scholarship_id
        """, (title, description, eligibility))
        scholarship_id = cur.fetchone()[0]

        # Insert questions
        for question_text, question_type in zip(questions, question_types):
            cur.execute("""
                INSERT INTO questions (scholarship_id, question_text, question_type)
                VALUES (%s, %s, %s)
            """, (scholarship_id, question_text, question_type))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('create_form.html')

@app.route('/apply/<int:scholarship_id>', methods=['GET', 'POST'])
def apply_scholarship(scholarship_id):
    if 'student_id' not in session:
        return redirect(url_for('login_student'))

    conn = get_db_connection()
    cur = conn.cursor()
    student_id = session['student_id']

    if request.method == 'POST':
        answers = request.form.getlist('answers[]')

        # Insert application and get the application_id
        cur.execute("""
            INSERT INTO scholarship_applications (student_id, scholarship_id, applied_on, status)
            VALUES (%s, %s, NOW(), 'Pending')
            RETURNING application_id
        """, (student_id, scholarship_id))
        application_id = cur.fetchone()[0]

        # Get related question IDs
        cur.execute("SELECT scholarship_id FROM questions WHERE scholarship_id = %s ORDER BY scholarship_id", (scholarship_id,))
        question_ids = [row[0] for row in cur.fetchall()]

        # Store answers
        for question_id, answer in zip(question_ids, answers):
            cur.execute("""
                INSERT INTO answers (student_id, scholarship_id, question_id, answer_text)
                VALUES (%s, %s, %s, %s)
            """, (student_id, scholarship_id, question_id, answer))

        pdf_filename = f"{student_id}_{application_id}.pdf"
        pdf_path = os.path.join('static', 'applications', pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 800, f"Student ID: {student_id}")
        c.drawString(100, 780, f"Scholarship ID: {scholarship_id}")
        c.drawString(100, 760, "Answers:")
        y = 740
        for i, answer in enumerate(answers):
            c.drawString(120, y, f"Q{i+1}: {answer}")
            y -= 20
            if y < 50:  #moving to next page if content is too long
                c.showPage()
                y = 800
        c.save()

        cur.execute("""
              UPDATE scholarship_applications
              SET application_pdf = %s
              WHERE application_id = %s
        """, (pdf_filename, application_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('student_dashboard'))

    cur.execute("SELECT title, description, eligibility FROM scholarships WHERE scholarship_id = %s", (scholarship_id,))
    scholarship = cur.fetchone()

    cur.execute("SELECT scholarship_id, question_text, question_type FROM questions WHERE scholarship_id = %s", (scholarship_id,))
    questions = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('apply_form.html', scholarship=scholarship, questions=questions)

@app.route('/review_application/<int:app_id>', methods=['POST'])
def review_application(app_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))

    decision = request.form['decision']
    review_letter = request.form['review_letter']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE scholarship_applications
        SET status=%s, review_letter=%s
        WHERE application_id=%s
    ''', (decision, review_letter, app_id))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('admin_review'))
@app.route('/admin/delete_scholarship/<int:scholarship_id>', methods=['POST'])
def delete_scholarship(scholarship_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))

    conn = get_db_connection()
    cur = conn.cursor()

    #checking if the scholarship exists
    cur.execute('SELECT * FROM scholarships WHERE scholarship_id = %s', (scholarship_id,))
    scholarship = cur.fetchone()

    if scholarship:
        # Delete related applications from scholarship_applications table
        cur.execute('DELETE FROM scholarship_applications WHERE scholarship_id = %s', (scholarship_id,))

        # Delete the scholarship itself
        cur.execute('DELETE FROM scholarships WHERE scholarship_id = %s', (scholarship_id,))

        conn.commit()
        cur.close()
        conn.close()

        return redirect('/admin_dashboard')  # Redirect to admin dashboard after deletion
    else:
        cur.close()
        conn.close()
        return 'Scholarship not found.'
@app.route('/manage_scholarships')
def manage_scholarships():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT scholarship_id, title FROM scholarships')
    scholarships = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('manage_scholarships.html', scholarships=scholarships)

@app.route('/admin_manage', methods=['GET', 'POST'])
def admin_manage():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        action = request.form['action']

        if action == 'delete':
            selected_admins = request.form.getlist('selected_admins')  #getting the selected admins ID
            if selected_admins:
                for admin_id in selected_admins:
                    cur.execute("DELETE FROM admins WHERE admin_id = %s",(admin_id,))  #here this delete will call the trigger for backup
        
        elif action == 'insert':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            cur.execute("SELECT insert_admins(%s, %s, %s)",(name, email, password))  #function for insertion
        
        elif action == 'update':
          selected_admins = request.form.getlist('selected_admins')
          if selected_admins:
              admin_id = selected_admins[0]
              name = request.form['name']
              email = request.form['email']
              password = request.form['password']
              cur.execute("CALL update_admins(%s, %s, %s, %s)", (admin_id, name, email, password))
              conn.commit()


        elif action == 'undo':
            selected_backups = request.form.getlist('selected_backups')
            for backup_id in selected_backups:
                if backup_id.strip():  # Only proceed if not empty
                    backup_id = int(backup_id)  # Ensure it's an integer
                    # Restore from backup
                    cur.execute('''
                        INSERT INTO admins (admin_id, name, email, password, created_at) 
                        SELECT admin_id, name, email, password, NOW() 
                        FROM admins_backup 
                        WHERE admin_id = %s
                    ''', (backup_id,))
                    # Delete from backup
                    cur.execute('DELETE FROM admins_backup WHERE admin_id = %s', (backup_id,))
            conn.commit()


    #fetching data
    cur.execute('SELECT * FROM admins ORDER BY admin_id')
    admins = cur.fetchall()
    cur.execute('SELECT * FROM admins_backup ORDER BY deleted_at DESC')
    backups = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin_manage.html', admins=admins, backups=backups)

@app.route('/student_manage', methods=['GET', 'POST'])
def student_manage():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        action = request.form['action']

        if action == 'delete':
            selected_students = request.form.getlist('selected_students')
            if selected_students:
                for student_id in selected_students:
                  cur.execute("DELETE FROM students WHERE student_id = %s",(student_id,))

        elif action == 'insert':
            student_name = request.form['student_name']
            email = request.form['email']
            student_pass = request.form['student_pass']
            grade = request.form.get('grade')
            gpa = request.form.get('GPA') 
            faculty = request.form.get('faculty')
            major_field = request.form.get('major_field')
            if grade == '' or grade is None:
                grade = None
            if gpa == '' or gpa is None:
                gpa = None

            cur.execute("SELECT insert_student(%s, %s, %s, %s, %s, %s, %s)",(student_name, email, student_pass, grade, gpa, faculty, major_field))

        elif action == 'update':
            selected_students = request.form.getlist('selected_students')
            if selected_students:
                student_id = int(selected_students[0])  # Ensure student_id is an integer
                student_name = request.form['student_name']
                email = request.form['email']
                student_pass = request.form['student_pass']
                grade = request.form.get('grade')
                gpa = request.form.get('GPA')
                faculty = request.form.get('faculty')
                major_field = request.form.get('major_field')
                
                if grade == '' or grade is None:
                    grade = None
                if gpa == '' or gpa is None:
                    gpa = None

                cur.execute("CALL update_students(%s, %s, %s, %s, %s, %s, %s, %s)", 
                            (student_id, student_name, email, student_pass, grade, gpa, faculty, major_field))


        elif action == 'undo':
            selected_backups = request.form.getlist('selected_backups')
            for backup_id in selected_backups:
                cur.execute('DELETE FROM students_backup WHERE student_id=%s', (backup_id,))

        conn.commit()

    cur.execute('SELECT * FROM students ORDER BY student_id')
    students = cur.fetchall()
    cur.execute('SELECT * FROM students_backup ORDER BY deleted_at DESC')

    backups = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('student_manage.html', students=students, backups=backups)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)