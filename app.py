from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import auth
import database
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'  # Guarda sesión en el servidor
socketio = SocketIO(app)

# Diccionario para almacenar las ubicaciones actuales de estudiantes
student_locations = {}

# Página inicial (Login)
@app.route('/')
def home():
    return render_template('login.html')

# Ruta para el login del docente
@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    username = request.form['username']
    password = request.form['password']
    if auth.authenticate_teacher(username, password):
        session.permanent = True  # Hace que la sesión persista
        session['user_type'] = 'teacher'
        return redirect(url_for('teacher_dashboard'))
    return "Login de docente incorrecto."

# Ruta para el login del estudiante
@app.route('/student_login', methods=['POST'])
def student_login():
    student_name = request.form['student_name']
    if auth.register_student(student_name):
        session['user_type'] = 'student'
        session['student_name'] = student_name
        return redirect(url_for('student_dashboard'))
    return "Login de estudiante incorrecto."

# Dashboard del docente
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_type' in session and session.get('user_type') == 'teacher':
        return render_template('teacher_dashboard.html', locations=student_locations)
    return redirect(url_for('home'))

# Dashboard del estudiante
@app.route('/student_dashboard')
def student_dashboard():
    if 'user_type' in session and session.get('user_type') == 'student':
        return render_template('student_dashboard.html', student_name=session.get('student_name'))
    return redirect(url_for('home'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()  # Limpia la sesión
    return redirect(url_for('home'))  # Redirige al login

# WebSocket para actualizaciones de ubicación
@socketio.on('update_location')
def handle_update_location(data):
    student_name = data['student_name']
    latitude = data['latitude']
    longitude = data['longitude']
    student_locations[student_name] = {'latitude': latitude, 'longitude': longitude}
    emit('location_update', student_locations, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
