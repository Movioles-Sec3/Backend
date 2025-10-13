"""
Router de administración para monitoreo del sistema
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, get_sync_status
import config

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/sync-status")
def sync_status():
    """Ver estado de la sincronización"""
    try:
        status = get_sync_status()
        
        return {
            "cloud_configured": status['cloud_configured'],
            "internet_available": status['internet_available'],
            "sync_queue_size": status['queue_size'],
            "sync_thread_running": status['sync_thread_alive'],
            "database_mode": config.DATABASE_MODE,
            "auto_sync_enabled": config.AUTO_SYNC_TO_CLOUD,
            "message": get_status_message(status)
        }
    except Exception as e:
        return {
            "error": str(e),
            "cloud_configured": False
        }

def get_status_message(status):
    """Obtener mensaje descriptivo del estado"""
    if not status['cloud_configured']:
        return "Sincronización no configurada"
    
    if status['queue_size'] == 0 and status['internet_available']:
        return "✅ Todo sincronizado"
    
    if status['queue_size'] > 0 and status['internet_available']:
        return f"🔄 Sincronizando {status['queue_size']} operaciones pendientes"
    
    if not status['internet_available']:
        return f"⏳ Sin conexión - {status['queue_size']} operaciones en cola esperando internet"
    
    return "Estado desconocido"

@router.get("/health")
def health():
    """Verificar salud del sistema"""
    return {
        "status": "ok",
        "database_mode": config.DATABASE_MODE,
        "sync_enabled": config.AUTO_SYNC_TO_CLOUD
    }

@router.get("/config")
def get_config():
    """Ver configuración actual"""
    return {
        "database_mode": config.DATABASE_MODE,
        "auto_sync_to_cloud": config.AUTO_SYNC_TO_CLOUD,
        "server_host": config.SERVER_HOST,
        "server_port": config.SERVER_PORT
    }
