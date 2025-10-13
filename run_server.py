"""
Script para ejecutar el servidor de desarrollo
Ejecutar con: python run_server.py
"""

import uvicorn
import config

if __name__ == "__main__":
    print("🚀 Iniciando servidor TapAndToast...")
    print(f"📊 Modo de base de datos: {config.DATABASE_MODE}")
    print(f"🔄 Sincronización automática: {'✅ Habilitada' if config.AUTO_SYNC_TO_CLOUD else '❌ Deshabilitada'}")
    print(f"📖 Documentación disponible en: http://{config.SERVER_HOST}:{config.SERVER_PORT}/docs")
    print("🔄 Recarga automática habilitada")
    
    uvicorn.run(
        "main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=True,
        log_level="info"
    )
