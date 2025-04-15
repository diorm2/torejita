import sqlite3

def connect_db():
    conn = sqlite3.connect('students.db')
    return conn

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS practices (
            id INTEGER PRIMARY KEY,
            student_name TEXT,
            practice_details TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_practice(student_name, practice_details, latitude, longitude):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO practices (student_name, practice_details, latitude, longitude)
        VALUES (?, ?, ?, ?)
    ''', (student_name, practice_details, latitude, longitude))
    conn.commit()
    conn.close()

def get_all_practices():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM practices')
    practices = cursor.fetchall()
    conn.close()
    return practices

# Crear la tabla al inicio
create_table()

