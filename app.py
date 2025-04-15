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
    if 'RENDER' in os.environ:  # Detecta si está en Render
        db_url = os.environ.get('DATABASE_URL')
        return db_url.replace('postgres://', 'postgresql://') + '?sslmode=require'
    return 'sqlite:///app.db'  # Usa SQLite localmente

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,    # Soluciona desconexiones en Render
    'pool_recycle': 300       # Recicla conexiones cada 5 minutos
}
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)

# ===================
# MODELOS (Se mantienen igual)
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
# MIDDLEWARE MEJORADO
# ============================
@app.before_request
def before_request():
    # Redirección HTTPS solo en producción
    if 'RENDER' in os.environ and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'), 301)
    
    # Inicialización de la base de datos para Render
    if 'RENDER' in os.environ and not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
            app.db_initialized = True

# ======================
# RUTAS (Se mantienen igual)
# ======================
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    # ... (tu código existente sin cambios)

@app.route('/student_login', methods=['POST'])
def student_login():
    # ... (tu código existente sin cambios)

@app.route('/update_location', methods=['POST'])
def update_location():
    # ... (tu código existente sin cambios)

@app.route('/get_locations')
def get_locations():
    # ... (tu código existente sin cambios)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # ... (tu código existente sin cambios)

@app.route('/student_dashboard')
def student_dashboard():
    # ... (tu código existente sin cambios)

@app.route('/logout')
def logout():
    # ... (tu código existente sin cambios)

# ======================
# INICIALIZACIÓN MEJORADA
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

# Solo inicializa localmente (Render usa PRE_START_COMMAND)
if __name__ == '__main__':
    initialize_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
