users = {
    "teacher": {"username": "docente", "password": "1234"},  # Usuario docente
    "students": {}  # Usuarios estudiantes
}

def authenticate_teacher(username, password):
    return username == users["teacher"]["username"] and password == users["teacher"]["password"]

def register_student(student_name):
    if student_name not in users["students"]:
        users["students"][student_name] = {"name": student_name}
        return True
    return False
