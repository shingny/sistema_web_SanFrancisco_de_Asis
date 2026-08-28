# Archivo de entrada WSGI para Alwaysdata (Phusion Passenger).
#
# Alwaysdata no ejecuta `python app.py`; los sitios Python se sirven
# mediante WSGI/Passenger usando este archivo. En tu panel de Alwaysdata:
#   - Tipo de sitio: Python
#   - Application path: la carpeta `microservicio-separado/`
#   - Entry point: passenger_wsgi.py
#
# Importa la aplicación Flask `app` creada en app.py (create_app()).

from app import app as application