import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# =============================================
# CONFIGURACIÓN HÍBRIDA (Local + Render)
# =============================================
app = Flask(__name__)

# Configuración de la base de datos (auto-adaptable)
def get_database_uri():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return db_url.replace('postgres://', 'postgresql://') + '?sslmode=require'
    print("ADVERTENCIA: DATABASE_URL no está configurada. Usando SQLite local.")
    return 'sqlite:///app.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)

# ===================
# MODELOS
# ===================
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

# ============================
# MIDDLEWARE
# ============================
@app.before_request
def before_request():
    # Redirección HTTPS solo en Render
    if 'RENDER' in os.environ and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'), 301)

# ======================
# RUTAS
# ======================
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    username = request.form.get('username')
    password = request.form.get('password')
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher and check_password_hash(teacher.password, password):
        session['user'] = teacher.username
        print(f"Inicio de sesión exitoso para: {username}")
        return redirect(url_for('teacher_dashboard'))
    return render_template('login.html', error="Usuario o contraseña incorrectos")

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('teacher_dashboard.html')

@app.route('/student_login', methods=['POST'])
def student_login():
    student_name = request.form.get('name')
    student = Student.query.filter_by(name=student_name).first()
    if student:
        session['student'] = student.name
        print(f"Inicio de sesión exitoso para: {student_name}")
        return redirect(url_for('student_dashboard'))
    return render_template('login.html', error="Estudiante no encontrado")

@app.route('/student_dashboard')
def student_dashboard():
    if 'student' not in session:
        return redirect(url_for('home'))
    return render_template('student_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ======================
# INICIALIZACIÓN
# ======================
def initialize_database():
    with app.app_context():
        db.create_all()
        if not Teacher.query.first():
            demo_teacher = Teacher(
                username="profesor",
                password=generate_password_hash("password")
            )
            db.session.add(demo_teacher)
            db.session.commit()

        if not Student.query.first():
            demo_student = Student(
                name="estudiante_demo",
                lat=0.0,
                lng=0.0
            )
            db.session.add(demo_student)
            db.session.commit()

# Solo inicializa localmente (Render usa PRE_START_COMMAND)
if __name__ == '__main__':
    initialize_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
