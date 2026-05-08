from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'devops-secret-key-2024'

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'rootpass'),
        database=os.environ.get('DB_NAME', 'studentdb')
    )

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        roll = request.form.get('roll', '').strip()
        department = request.form.get('department', '').strip()
        gpa = request.form.get('gpa', '').strip()

        if not name or not email or not roll:
            flash('Name, Email and Roll No are required!', 'error')
            return render_template('add.html')

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO students (name,  roll_no,email, department, gpa) VALUES (%s, %s, %s, %s, %s)",
                (name, email, roll, department, gpa or None)
            )
            conn.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        except mysql.connector.IntegrityError:
            flash('Email or Roll No already exists!', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('add.html')

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        gpa = request.form.get('gpa', '').strip()

        cursor.execute(
            "UPDATE students SET name=%s, email=%s, department=%s, gpa=%s WHERE id=%s",
            (name, email, department, gpa or None, student_id)
        )
        conn.commit()
        flash('Student updated successfully!', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('index'))

    return render_template('edit.html', student=student)

@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM students WHERE name LIKE %s OR email LIKE %s OR roll_no LIKE %s",
        (f'%{query}%', f'%{query}%', f'%{query}%')
    )
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', students=students, search_query=query)

@app.route('/student/<int:student_id>')
def view_student(student_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('index'))
    return render_template('view.html', student=student)

@app.route('/api/students')
def api_students():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
