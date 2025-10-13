"""
Configuración centralizada de la aplicación
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Modo de base de datos: 'local' o 'cloud'
DATABASE_MODE = os.getenv("DATABASE_MODE", "local")

# URLs de base de datos
LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "sqlite:///./tapandtoast.db")
CLOUD_DATABASE_URL = os.getenv("CLOUD_DATABASE_URL", "")

# Replicación automática
AUTO_SYNC_TO_CLOUD = os.getenv("AUTO_SYNC_TO_CLOUD", "false").lower() == "true"

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-muy-segura-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Servidor
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

def get_database_url():
    """Obtener la URL de base de datos según el modo configurado"""
    if DATABASE_MODE == "cloud":
        if not CLOUD_DATABASE_URL:
            raise ValueError("CLOUD_DATABASE_URL no está configurada")
        return CLOUD_DATABASE_URL
    return LOCAL_DATABASE_URL

def is_sqlite():
    """Verificar si se está usando SQLite"""
    return get_database_url().startswith("sqlite")

def is_postgresql():
    """Verificar si se está usando PostgreSQL"""
    return get_database_url().startswith("postgresql")
