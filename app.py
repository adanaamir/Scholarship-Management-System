from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from datetime import datetime
import psycopg2.extras

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

# ----------------------
# Home, Registration, Login (unchanged) for commit
# ----------------------
#please ho jao
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
        <h1>Welcome to the Portal</h1>
        <div class="button-container">
            <a href="/login_student">Login as Student</a>
            <a href="/login_admin">Login as Admin</a>
            <a href="/admin_manage">Manage Admins (Admin Only)</a>
            <a href="/register_student">Register as Student</a>
            <a href="/register_admin">Register as Admin</a>
        </div>
    </body>
    </html>
    '''

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO Students (name, email, password) VALUES (%s, %s, %s)',
                    (name, email, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login_student')

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Student Registration</title>
      <style>
        body {
          background-color: #f8f9fa;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
        }
        .card {
          background: #fff;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          width: 320px;
          text-align: center;
        }
        .card h1 {
          margin-bottom: 20px;
          font-size: 28px;
          color: #333;
        }
        .card input {
          width: 100%;
          padding: 10px;
          margin-bottom: 15px;
          border: 1px solid #ccc;
          border-radius: 5px;
          font-size: 16px;
        }
        .card button {
          width: 100%;
          padding: 12px;
          background-color: #007bff;
          border: none;
          border-radius: 5px;
          color: #fff;
          font-size: 18px;
          cursor: pointer;
          transition: background 0.3s ease;
        }
        .card button:hover {
          background-color: #0056b3;
        }
        .card .home-link {
          margin-top: 20px;
          font-size: 14px;
        }
        .card .home-link a {
          color: #007bff;
          text-decoration: none;
        }
        .card .home-link a:hover {
          text-decoration: underline;
        }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Student Registration</h1>
        <form method="post">
          <input type="text" name="name" placeholder="Your Name" required>
          <input type="email" name="email" placeholder="Your Email" required>
          <input type="password" name="password" placeholder="Your Password" required>
          <button type="submit">Register</button>
        </form>
        <div class="home-link">
          <a href="/">← Back to Home</a>
        </div>
      </div>
    </body>
    </html>
    '''

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
    
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Admin Registration</title>
      <style>
        body {
          background-color: #f8f9fa;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
        }
        .card {
          background: #fff;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          width: 320px;
          text-align: center;
        }
        .card h1 {
          margin-bottom: 20px;
          font-size: 28px;
          color: #333;
        }
        .card input {
          width: 100%;
          padding: 10px;
          margin-bottom: 15px;
          border: 1px solid #ccc;
          border-radius: 5px;
          font-size: 16px;
        }
        .card button {
          width: 100%;
          padding: 12px;
          background-color: #007bff;
          border: none;
          border-radius: 5px;
          color: #fff;
          font-size: 18px;
          cursor: pointer;
          transition: background 0.3s ease;
        }
        .card button:hover {
          background-color: #0056b3;
        }
        .card .home-link {
          margin-top: 20px;
          font-size: 14px;
        }
        .card .home-link a {
          color: #007bff;
          text-decoration: none;
        }
        .card .home-link a:hover {
          text-decoration: underline;
        }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Admin Registration</h1>
        <form method="post">
          <input type="text" name="name" placeholder="Your Name" required>
          <input type="email" name="email" placeholder="Your Email" required>
          <input type="password" name="password" placeholder="Your Password" required>
          <button type="submit">Register</button>
        </form>
        <div class="home-link">
          <a href="/">← Back to Home</a>
        </div>
      </div>
    </body>
    </html>
    '''

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM Students WHERE email=%s AND password=%s', (email, password))
        student = cur.fetchone()
        cur.close()
        conn.close()

        if student:
            session['student_id'] = student[0]
            session['email'] = email
            session['user_type'] = 'student'
            return redirect('/student_dashboard')
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
        return redirect('/login_student')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(''' 
        SELECT status, review_letter FROM scholarship_applications
        WHERE student_id = %s ORDER BY applied_on DESC LIMIT 1
    ''', (session['student_id'],))
    result = cur.fetchone()
    conn.close()

    if result:
        scholarship_status = result[0]
        review_letter = result[1]
    else:
        scholarship_status = 'Pending'
        review_letter = None

    return render_template('student_dashboard.html', email=session['email'],
                           scholarship_status=scholarship_status,
                           review_letter=review_letter)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))

    return render_template('admin_dashboard.html')

@app.route('/admin_review')
def admin_review():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login_admin'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    SELECT id, name, email, reg_no, program, department, curr_cgpa, status
    FROM scholarship_applications
    WHERE status = 'Pending'
    ORDER BY applied_on DESC
''')

    applications = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin_review.html', applications=applications)
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

@app.route('/scholarship_form', methods=['GET', 'POST'])
def scholarship_form():
    if request.method == 'POST':
        # Extracting the form data
        name = request.form['name']
        email = request.form['email']
        reg_no = request.form['reg_no']
        nic = request.form['nic']
        dob_day = int(request.form['dob_day'])
        
        # Map the month name to its integer value
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        dob_month_str = request.form['month']
        dob_month = month_map[dob_month_str]  # Convert month name to month number
        dob_year = int(request.form['year'])

        # Create the dob in the required format
        dob = f"{dob_year}-{dob_month:02d}-{dob_day:02d}"

        # Print the form data to debug
        print(request.form)

        conn = get_db_connection()
        cur = conn.cursor()

        # Ensure that all form data exists (use .get() for optional fields)
        cur.execute('''
            INSERT INTO scholarship_applications (student_id, scholarship_type, name, email, reg_no, nic, dob, semester, program, department, curr_gpa, curr_cgpa, prev_gpa, address, phone_number, guardian_name, guardian_contact, relation, has_other_scholarship, status, applied_on)
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
        conn.close()

        return redirect(url_for('student_dashboard'))  # Redirect to the student dashboard

    # Data to populate the form fields (for dropdowns)
    Month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    Year = list(range(1990, datetime.now().year + 1))
    Semester = [f"Semester {i}" for i in range(1, 9)]
    Program = ["BS Computer Science", "BS Mathematics", "BBA", "MBA", "Electrical Engineering"]
    Department = ["CS", "Math", "Business", "Electrical"]

    return render_template('scholarship_form.html', Month=Month, Year=Year, Semester=Semester, Program=Program, Department=Department)

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
        WHERE id=%s
    ''', (decision, review_letter, app_id))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('admin_review'))


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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
