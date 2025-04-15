import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# =============================================
# CONFIGURACIÓN PARA RENDER (POSTGRESQL + HTTPS)
# =============================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') + '?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)

# ===================
# MODELOS DE DATABASE
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
# MIDDLEWARE PARA HTTPS EN RENDER
# ============================
@app.before_request
def enforce_https():
    if not request.is_secure and 'render.com' in request.host:
        return redirect(request.url.replace('http://', 'https://'), 301)

# ==============
# RUTAS PRINCIPALES
# ==============
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher and check_password_hash(teacher.password, password):
        session['user_type'] = 'teacher'
        return redirect(url_for('teacher_dashboard'))
    return "Credenciales incorrectas", 401

@app.route('/student_login', methods=['POST'])
def student_login():
    name = request.form.get('student_name')
    if name:
        student = Student(name=name, lat=None, lng=None)
        db.session.add(student)
        db.session.commit()
        
        session['user_type'] = 'student'
        session['student_name'] = name
        return redirect(url_for('student_dashboard'))
    return "Nombre inválido", 400

# ======================
# API PARA UBICACIONES (REEMPLAZA WEBSOCKETS)
# ======================
@app.route('/update_location', methods=['POST'])
def update_location():
    if session.get('user_type') != 'student':
        return "No autorizado", 403
    
    student = Student.query.filter_by(name=session['student_name']).first()
    if student:
        student.lat = request.json.get('lat')
        student.lng = request.json.get('lng')
        db.session.commit()
        return "Ubicación actualizada", 200
    return "Estudiante no encontrado", 404

@app.route('/get_locations')
def get_locations():
    if session.get('user_type') != 'teacher':
        return "No autorizado", 403
    
    locations = {s.name: {'lat': s.lat, 'lng': s.lng} 
                for s in Student.query.all()}
    return jsonify(locations)

# ======================
# DASHBOARDS
# ======================
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('user_type') != 'teacher':
        return redirect(url_for('home'))
    return render_template('teacher_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect(url_for('home'))
    return render_template('student_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ======================
# INICIALIZACIÓN
# ======================
with app.app_context():
    db.create_all()
    # Crear usuario docente demo (eliminar en producción)
    if not Teacher.query.first():
        demo_teacher = Teacher(
            username="profesor",
            password=generate_password_hash("password")
        )
        db.session.add(demo_teacher)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)