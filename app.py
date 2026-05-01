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
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin_main' and password == 'admin123':
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session: return redirect(url_for('login'))
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

# --- ADD STUDENT ---
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

# --- ADD FACULTY (NEW) ---
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
        res = "🎓 <b>Student Found:</b> Pratibha (S1003), BTECH-AIML. Lead of AI Club."
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