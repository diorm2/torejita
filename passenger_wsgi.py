import os
import sys
from app import app, socketio  # Importamos tanto 'app' como 'socketio' desde app.py

# Configura el entorno virtual (si lo usas)
INTERP = os.path.expanduser("~/venv/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Define la aplicación WSGI para Passenger
application = app  # 'app' es tu instancia de Flask

# Opcional: Si SocketIO requiere configuración adicional
if __name__ == "__main__":
    socketio.run(application)