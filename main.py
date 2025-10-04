from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import usuario, producto, compra
from routers import analytics

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="TapAndToast API",
    description="Backend para la aplicación móvil TapAndToast - Sistema de pedidos para bares",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde la app móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(usuario.router)
app.include_router(producto.router)
app.include_router(compra.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    """Endpoint de bienvenida"""
    return {
        "mensaje": "¡Bienvenido a TapAndToast API!",
        "version": "1.0.0",
        "documentacion": "/docs"
    }

@app.get("/health")
def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "ok", "mensaje": "El servidor está funcionando correctamente"}
