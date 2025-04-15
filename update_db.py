import sqlite3

def update_table():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    try:
        # Añadir columnas latitude y longitude si no existen
        cursor.execute("ALTER TABLE practices ADD COLUMN latitude REAL")
        cursor.execute("ALTER TABLE practices ADD COLUMN longitude REAL")
        print("Columnas añadidas correctamente.")
    except sqlite3.OperationalError as e:
        print("Error:", e)
    conn.commit()
    conn.close()

update_table()
