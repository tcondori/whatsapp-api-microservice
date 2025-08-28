"""
Configuración de conexión a base de datos y extensiones SQLAlchemy
Gestiona conexiones, sesiones y migraciones de base de datos
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app
import logging

# Inicializar SQLAlchemy y Migrate
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """
    Inicializa la conexión a la base de datos y migraciones
    Args:
        app: Instancia de la aplicación Flask
    """
    # Configurar SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar logging de SQL en desarrollo
    if app.config.get('DEBUG'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Crear tablas si no existen 
    # Para PostgreSQL, las tablas ya están creadas con el script SQL
    # Para SQLite (testing), crear automáticamente
    if app.config.get('DEBUG'):
        database_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in database_uri:
            with app.app_context():
                db.create_all()
                logging.info("Tablas SQLite creadas/verificadas")
        elif 'postgresql' in database_uri:
            logging.info("Usando PostgreSQL - tablas ya creadas con script SQL")

def get_db_session():
    """
    Obtiene una sesión de base de datos independiente para operaciones fuera del contexto Flask
    Returns:
        Session: Sesión de SQLAlchemy
    """
    if current_app:
        # Si estamos en contexto Flask, usar la configuración de la app
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    else:
        # Fallback para casos sin contexto
        database_url = os.getenv('DATABASE_URL', 'sqlite:///whatsapp_dev.db')
        engine = create_engine(database_url)
    
    Session = sessionmaker(bind=engine)
    return Session()

def close_db_session(session):
    """
    Cierra una sesión de base de datos de forma segura
    Args:
        session: Sesión a cerrar
    """
    try:
        session.close()
    except Exception as e:
        logging.error(f"Error al cerrar sesión de base de datos: {e}")

# Funciones auxiliares para transacciones
def safe_commit(session):
    """
    Ejecuta commit de forma segura con manejo de errores
    Args:
        session: Sesión de base de datos
    Returns:
        bool: True si el commit fue exitoso
    """
    try:
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        # Convertir el error a string seguro para logging
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        logging.error(f"Error en commit de base de datos: {error_msg}")
        return False

def safe_rollback(session):
    """
    Ejecuta rollback de forma segura
    Args:
        session: Sesión de base de datos
    """
    try:
        session.rollback()
    except Exception as e:
        logging.error(f"Error en rollback de base de datos: {e}")
