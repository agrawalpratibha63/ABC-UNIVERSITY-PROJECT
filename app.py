from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'university_secret_key'

# --- MYSQL DATABASE CONNECTION ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="pilu9548",        
        database="newcase"  
    )

@app.route('/')
def home():
    if 'username' in session:
        if session['role'] == 'admin': return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'student': return redirect(url_for('student_dashboard'))
        elif session['role'] == 'lecturer': return redirect(url_for('lecturer_dashboard'))
    return redirect(url_for('login'))

# --- SMART LOGIN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 1. ADMIN LOGIN CHECK
        if username == 'admin_main' and password == 'admin123':
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 2. STUDENT LOGIN CHECK (Checks directly in 'students' table)
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (username,))
            student = cursor.fetchone()
            if student and password == 'student123':  # Default password for all students
                session['username'] = student['student_id']
                session['name'] = student['name']
                session['role'] = 'student'
                conn.close()
                return redirect(url_for('student_dashboard'))
                
            # 3. FACULTY LOGIN CHECK (Checks directly in 'lecturers' table)
            cursor.execute("SELECT * FROM lecturers WHERE lecturer_id = %s", (username,))
            lecturer = cursor.fetchone()
            if lecturer and password == 'faculty123':  # Default password for all faculty
                session['username'] = lecturer['lecturer_id']
                session['name'] = lecturer['name']
                session['role'] = 'lecturer'
                conn.close()
                return redirect(url_for('lecturer_dashboard'))
                
            conn.close()
        except Exception as e:
            print("Database Error:", e)
            
        return render_template('login.html', error='Invalid credentials. Check username or password.')
        
    return render_template('login.html')

# --- DASHBOARDS ---
@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin': return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.execute("SELECT * FROM lecturers")
        lecturers = cursor.fetchall()
        cursor.execute("SELECT * FROM programmes")
        programmes = cursor.fetchall()
        conn.close()
    except Exception as e:
        print("Error:", e)
        students, lecturers, programmes = [], [], []
    return render_template('admin_dashboard.html', students=students, lecturers=lecturers, programmes=programmes)

@app.route('/student')
def student_dashboard():
    if 'username' not in session or session['role'] != 'student': return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (session['username'],))
    student_data = cursor.fetchone()
    
    # Mocking courses for Student Dashboard
    mock_courses = [
        {"course_code": "CS101", "title": "Intro to Programming", "grade": "A+", "status": "Passed", "term_taken": "Fall", "year_taken": 2026},
        {"course_code": "AI201", "title": "Machine Learning Basics", "grade": "A", "status": "Passed", "term_taken": "Fall", "year_taken": 2026}
    ]
    conn.close()
    
    return render_template('student_dashboard.html', student=student_data, courses=mock_courses)

@app.route('/lecturer')
def lecturer_dashboard():
    if 'username' not in session or session['role'] != 'lecturer': return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lecturers WHERE lecturer_id = %s", (session['username'],))
    lecturer_data = cursor.fetchone()
    
    # Mocking courses and committees for Lecturer Dashboard
    mock_courses = [{"course_code": "AI201", "title": "Machine Learning Basics"}]
    mock_committees = [{"title": "Tech Fest Planning", "frequency": "Weekly"}]
    conn.close()
    
    return render_template('lecturer_dashboard.html', lecturer=lecturer_data, courses=mock_courses, committees=mock_committees)

# --- ADD STUDENT & FACULTY ROUTES ---
@app.route('/add_student', methods=['POST'])
def add_student():
    sid, name = request.form.get('student_id'), request.form.get('name')
    bday, year = request.form.get('birthday'), request.form.get('enrollment_year')
    pcode = request.form.get('programme_code')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (student_id, name, birthday, enrollment_year, programme_code) VALUES (%s, %s, %s, %s, %s)", (sid, name, bday, year, pcode))
    conn.commit()
    conn.close()
    flash(f"Student {name} added successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    fid, name = request.form.get('lecturer_id'), request.form.get('name')
    title, office = request.form.get('title'), request.form.get('office_room')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lecturers (lecturer_id, name, title, office_room) VALUES (%s, %s, %s, %s)", (fid, name, title, office))
    conn.commit()
    conn.close()
    flash(f"Faculty {title} {name} added successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# --- CHATBOT ---
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_msg = request.json.get('message', '').lower()
    if 'highest' in user_msg and 'cgpa' in user_msg:
        res = "📊 Based on records, <b>Pratibha Agrawal</b> has the highest SGPA of 9.2."
    elif 'pratibha' in user_msg:
        res = "🎓 <b>Student Found:</b> Pratibha Agrawal (S1003), BTECH-AIML. Lead of AI Club."
    elif 'sharma' in user_msg:
        res = "👨‍🏫 <b>Faculty Profile:</b> Dr. R.K. Sharma, Professor. Office: Block A-301."
    else:
        res = "I am your Smart ERP Assistant. Ask me about students, faculty, or toppers!"
    return jsonify({'reply': res})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)