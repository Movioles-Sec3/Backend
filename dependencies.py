from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import Usuario

# Dependencias comunes reutilizables

def get_db_session() -> Session:
    """Dependencia para obtener la sesión de base de datos"""
    return Depends(get_db)

def get_authenticated_user() -> Usuario:
    """Dependencia para obtener el usuario autenticado"""
    return Depends(get_current_user)

# Dependencias específicas para roles (para futuras implementaciones)
# def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
#     """Dependencia para verificar que el usuario es administrador"""
#     if not current_user.is_admin:  # Campo a agregar en el futuro
#         raise HTTPException(status_code=403, detail="Permisos insuficientes")
#     return current_user

# def get_staff_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
#     """Dependencia para verificar que el usuario es staff"""
#     if not current_user.is_staff:  # Campo a agregar en el futuro
#         raise HTTPException(status_code=403, detail="Permisos insuficientes")
#     return current_user
