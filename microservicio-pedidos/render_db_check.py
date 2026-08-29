"""Diagnóstico de arranque para Render.

Importa la app para forzar create_all()/seed y captura el traceback
completo si algo falla, de modo que aparezca en los logs de Render.
"""
import traceback

try:
    from app import app
except Exception:
    traceback.print_exc()
    raise

if __name__ == "__main__":
    # Verificar la URI que SQLAlchemy usa realmente
    from sqlalchemy import create_engine, text
    from config import Config, _sqlalchemy_uri
    print("=== DEBUG: SQLALCHEMY_DATABASE_URI ===")
    print(_sqlalchemy_uri())
    print("=== DEBUG: comprobando conexión ===")
    try:
        engine = create_engine(_sqlalchemy_uri())
        with engine.connect() as conn:
            print("CONEXION OK:", conn.execute(text("select version()")).scalar())
    except Exception:
        traceback.print_exc()
        raise
