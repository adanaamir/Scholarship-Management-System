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
        dbname="Students_db",
        user="postgres",
        password="pepsi123",
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
        cur.execute('INSERT INTO students (student_name, email, student_pass) VALUES (%s, %s, %s)',
                    (name, email, password))
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
        cur.execute('INSERT INTO admin (name, email, password, created_at) VALUES (%s, %s, %s, %s)',
                    (name, email, password, datetime.now().date()))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login_admin')
    
    return render_template('register_admin.html')



##
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
        cur.execute('SELECT * FROM admin WHERE email=%s AND password=%s', (email, password))
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

    # Show scholarships the student has NOT applied to
    cur.execute("""
        SELECT s.id, s.title FROM scholarships s
        WHERE s.id NOT IN (
            SELECT scholarship_id FROM scholarship_applications WHERE student_id = %s
        )
    """, (student_id,))
    scholarships = cur.fetchall()

    # Show all applications by the student with their current status and review letter
    cur.execute("""
        SELECT sa.application_id, sa.status, sa.review_letter, sa.application_date, sa.applied_on, sc.title
        FROM scholarship_applications sa
        JOIN scholarships sc ON sa.scholarship_id = sc.id
        WHERE sa.student_id = %s
    """, (student_id,))
    applications = cur.fetchall()

    cur.close()

    cur.execute(''' 
        SELECT status, review_letter FROM scholarship_applications
        WHERE student_id = %s ORDER BY submitted_at DESC LIMIT 1
    ''', (session['student_id'],))
    result = cur.fetchone()
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
            VALUES (%s, %s, %s) RETURNING id
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
        cur.execute("SELECT id FROM questions WHERE scholarship_id = %s ORDER BY id", (scholarship_id,))
        question_ids = [row[0] for row in cur.fetchall()]

##
@app.route('/scholarship_form', methods=['GET', 'POST'])
def scholarship_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        reg_no = request.form['reg_no']
        nic = request.form['nic']
        dob_day = int(request.form['dob_day'])
        
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        dob_month_str = request.form['month']
        dob_month = month_map[dob_month_str]  # Convert month name to month number
        dob_year = int(request.form['year'])

        dob = f"{dob_year}-{dob_month:02d}-{dob_day:02d}"

        print(request.form)

        # Store answers
        for question_id, answer in zip(question_ids, answers):
            cur.execute("""
                INSERT INTO answers (student_id, scholarship_id, question_id, answer_text)
                VALUES (%s, %s, %s, %s)
            """, (student_id, scholarship_id, question_id, answer))

        # ✅ Generate and save PDF
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
            if y < 50:  # Move to next page if content is too long
                c.showPage()
                y = 800
        c.save()

        # ✅ Store PDF path in DB
        cur.execute("""
            UPDATE scholarship_applications
            SET application_pdf = %s
            WHERE application_id = %s
        """, (pdf_filename, application_id))

        cur.execute('''
            INSERT INTO scholarship_applications (student_id, scholarship_type, name, email, reg_no, nic, dob, semester, 
            program, department, curr_gpa, curr_cgpa, prev_gpa, address, phone_number, guardian_name, guardian_contact, relation, 
            has_other_scholarship, status, applied_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (
            session['student_id'], 'Merit Based', name, email, reg_no, nic, dob,
            request.form.get('Semester', ''), request.form.get('Program', ''), request.form.get('Department', ''), 
            request.form.get('curr_gpa', None), request.form.get('curr_cgpa', None),
            request.form.get('prev_gpa', None), request.form.get('address', ''), request.form.get('phone_number', ''),
            request.form.get("guardian's_name", ''), request.form.get("guardian's_contact", ''),
            request.form.get('relation', ''), request.form.get('yesNo', ''), 'Pending'
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('student_dashboard'))

    cur.execute("SELECT title, description, eligibility FROM scholarships WHERE id = %s", (scholarship_id,))
    scholarship = cur.fetchone()

    cur.execute("SELECT id, question_text, question_type FROM questions WHERE scholarship_id = %s", (scholarship_id,))
    questions = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('apply_form.html', scholarship=scholarship, questions=questions)

def fetchStudentData():
  try:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        UPDATE scholarship_applications
        SET status=%s, review_letter=%s
        WHERE application_id=%s
    ''', (decision, review_letter, app_id))
    conn.commit()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
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

    # Check if the scholarship exists
    cur.execute('SELECT * FROM scholarships WHERE id = %s', (scholarship_id,))
    scholarship = cur.fetchone()

    if scholarship:
        # Delete related applications from scholarship_applications table
        cur.execute('DELETE FROM scholarship_applications WHERE scholarship_id = %s', (scholarship_id,))

        # Delete the scholarship itself
        cur.execute('DELETE FROM scholarships WHERE id = %s', (scholarship_id,))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('create_form.html')

    return redirect(url_for('admin_review'))
@app.route('/admin/delete_scholarship/<int:scholarship_id>', methods=['POST'])
def delete_scholarship(scholarship_id):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if the scholarship exists
    cur.execute('SELECT * FROM scholarships WHERE id = %s', (scholarship_id,))
    scholarship = cur.fetchone()

    if scholarship:
        # Delete related applications from scholarship_applications table
        cur.execute('DELETE FROM scholarship_applications WHERE scholarship_id = %s', (scholarship_id,))

        # Delete the scholarship itself
        cur.execute('DELETE FROM scholarships WHERE id = %s', (scholarship_id,))

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
    cur.execute('SELECT id, title FROM scholarships')
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

        # Handle "Delete" action
        if action == 'delete':
            selected_admins = request.form.getlist('selected_admins')  # Get the selected admin IDs
            if selected_admins:
                for admin_id in selected_admins:
                    # Backup before deleting
                    cur.execute(''' 
                        INSERT INTO admin_backup (id, name, email, password, deleted_at) 
                        SELECT admin_id, name, email, password, NOW() 
                        FROM admin 
                        WHERE admin_id=%s
                    ''', (admin_id,))
                    # Delete the admin
                    cur.execute('DELETE FROM admin WHERE admin_id=%s', (admin_id,))
        
        # Handle "Insert" action (new admin insertion)
        elif action == 'insert':
            # Get the new admin details from the form
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            # Insert the new admin into the database
            cur.execute('INSERT INTO admin (name, email, password, created_at) VALUES (%s, %s, %s, %s)',
                        (name, email, password, datetime.now().date()))
        
        # Handle "Update" action (update selected admin)
        elif action == 'update':
          selected_admins = request.form.getlist('selected_admins')
          if selected_admins:
              admin_id = selected_admins[0]
              name = request.form['name']
              email = request.form['email']
              password = request.form['password']
              cur.execute('UPDATE admin SET name=%s, email=%s, password=%s WHERE admin_id=%s',
                          (name, email, password, admin_id))
              conn.commit()


        # Handle "Undo" action (restore deleted admin)
        elif action == 'undo':
            # Get the latest deleted admin(s) from admin_backup to restore
            selected_backups = request.form.getlist('selected_backups')
            for backup_id in selected_backups:
                # Restore from backup
                cur.execute('''
                    INSERT INTO admin (admin_id, name, email, password, created_at) 
                    SELECT id, name, email, password, NOW() 
                    FROM admin_backup 
                    WHERE id = %s
                ''', (backup_id,))
                # Delete from backup (undo the delete)
                cur.execute('DELETE FROM admin_backup WHERE id = %s', (backup_id,))


        conn.commit()

    # Fetch data
    cur.execute('SELECT * FROM admin ORDER BY admin_id')
    admins = cur.fetchall()
    cur.execute('SELECT * FROM admin_backup ORDER BY deleted_at DESC')
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
                    cur.execute('''
                        INSERT INTO students_backup (
                            student_id, student_name, email, student_pass,
                            registeration_date, grade, GPA, faculty, major_field
                        )
                        SELECT student_id, student_name, email, student_pass,
                               registeration_date, grade, GPA, faculty, major_field
                        FROM students
                        WHERE student_id=%s
                    ''', (student_id,))
                    cur.execute('DELETE FROM students WHERE student_id=%s', (student_id,))

        elif action == 'insert':
            student_name = request.form['student_name']
            email = request.form['email']
            student_pass = request.form['student_pass']
            grade = request.form.get('grade')
            gpa = request.form.get('GPA')
            faculty = request.form.get('faculty')
            major_field = request.form.get('major_field')

            cur.execute('''
                INSERT INTO students (student_name, email, student_pass, grade, GPA, faculty, major_field)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (student_name, email, student_pass, grade, gpa, faculty, major_field))

        elif action == 'update':
            selected_students = request.form.getlist('selected_students')
            if selected_students:
                student_id = selected_students[0]
                student_name = request.form['student_name']
                email = request.form['email']
                student_pass = request.form['student_pass']
                grade = request.form.get('grade')
                gpa = request.form.get('GPA')
                faculty = request.form.get('faculty')
                major_field = request.form.get('major_field')

                cur.execute('''
                    UPDATE students SET student_name=%s, email=%s, student_pass=%s,
                        grade=%s, GPA=%s, faculty=%s, major_field=%s
                    WHERE student_id=%s
                ''', (student_name, email, student_pass, grade, gpa, faculty, major_field, student_id))

        elif action == 'undo':
            selected_backups = request.form.getlist('selected_backups')
            for backup_id in selected_backups:
                cur.execute('''
                    INSERT INTO students (
                        student_id, student_name, email, student_pass,
                        registeration_date, grade, GPA, faculty, major_field
                    )
                    SELECT student_id, student_name, email, student_pass,
                           registeration_date, grade, GPA, faculty, major_field
                    FROM students_backup WHERE student_id=%s
                ''', (backup_id,))
                cur.execute('DELETE FROM students_backup WHERE student_id=%s', (backup_id,))

        conn.commit()

    cur.execute('SELECT * FROM students ORDER BY student_id')
    students = cur.fetchall()
    cur.execute('SELECT * FROM students_backup ORDER BY registeration_date DESC')
    backups = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('student_manage.html', students=students, backups=backups)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == '__main__':
    app.run(debug=True)