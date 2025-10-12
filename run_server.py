"""
Script para ejecutar el servidor de desarrollo
Ejecutar con: python run_server.py
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor TapAndToast...")
    print("📖 Documentación disponible en: http://localhost:8000/docs")
    print("🔄 Recarga automática habilitada")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
