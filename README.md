# TapAndToast Backend API

Backend para la aplicación móvil **TapAndToast** - Sistema de pedidos para bares que elimina las filas y mejora la experiencia del cliente.

## 🚀 Características

- **Sistema de Pedidos**: Los clientes pueden ver el menú, añadir productos al carrito y pagar desde la app
- **Monedero Digital**: Sistema de saldo prepagado para pagos rápidos
- **Códigos QR**: Generación automática de códigos únicos para cada orden
- **Gestión de Estados**: Seguimiento completo del estado de las órdenes (PAGADO → EN_PREPARACION → LISTO → ENTREGADO)
- **API RESTful**: Endpoints bien documentados para integración con la app móvil

## 🛠️ Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para manejo de base de datos
- **SQLite**: Base de datos para desarrollo local
- **PostgreSQL**: Base de datos en la nube con replicación automática
- **JWT**: Autenticación segura con tokens
- **Pydantic**: Validación de datos automática
- **Bcrypt**: Hash seguro de contraseñas

## 📁 Estructura del Proyecto

```
Backend/
├── main.py                           # Aplicación principal FastAPI - Inicializa la app y middlewares
├── database.py                       # Configuración dual de base de datos local + nube con sincronización asíncrona
├── models.py                         # Modelos SQLAlchemy ORM (Usuario, Producto, Compra, QR, etc.)
├── schemas.py                        # Esquemas Pydantic para validación de request/response
├── auth.py                           # Sistema de autenticación JWT + hash de contraseñas (bcrypt)
├── config.py                         # Configuración centralizada desde variables de entorno
├── dependencies.py                   # Dependencias reutilizables para inyección de dependencias
├── requirements.txt                  # Dependencias Python del proyecto
│
├── run_server.py                     # Script para ejecutar el servidor en desarrollo
├── seed_data.py                      # Script para poblar base de datos con datos de prueba
├── check_users.py                    # Verificar sincronización entre local y nube (sin emojis)
├── sync_to_cloud.py                  # Sincronización manual completa a la nube
├── watch_sync_status.py              # Monitor en tiempo real del estado de sincronización
├── test_offline_sync.py              # Test de sincronización sin conexión a internet
├── test_sync.py                      # Tests automatizados de la API
│
├── routers/                          # Endpoints organizados por recurso
│   ├── __init__.py
│   ├── usuario.py                    # Endpoints: POST /usuarios/, /usuarios/token, /usuarios/me
│   ├── producto.py                   # Endpoints: GET /productos/, POST /productos/
│   ├── compra.py                     # Endpoints: POST /compras/, GET /compras/me, /compras/qr/escanear
│   ├── conversion.py                 # Endpoints de conversión de moneda
│   ├── analytics.py                  # Endpoints: GET /analytics/reorden-por-categoria, /tiempo-promedio
│   └── admin.py                      # Endpoints de administración: /admin/sync-status, /admin/health
│
├── services/                         # Servicios reutilizables de negocio
│   ├── __init__.py
│   └── currency_service.py           # Servicio de conversión de monedas con caché
│
├── scripts/                          # Scripts utilitarios
│   ├── README.md
│   └── export_compras_tiempos.py     # Exportar análisis de tiempos de compras
│
├── .github/                          # Configuración de GitHub
│   └── copilot-instructions.md       # Instrucciones para AI agents (Copilot)
│
├── Documentación/
│   ├── README.md                     # Este archivo
│   ├── API_DOCUMENTATION.md          # Documentación completa de endpoints
│   ├── CONFIGURACION_COMPLETADA.md   # Guía de configuración inicial
│   ├── GUIA_RAPIDA.md                # Guía rápida de uso (5 minutos)
│   ├── CONFIGURACION_FINAL_COMPLETADA.md  # Resumen final del sistema
│   ├── SINCRONIZACION_OFFLINE.md     # Guía técnica del sistema de sync offline
│   ├── RESUMEN_SISTEMA_SYNC.md       # Resumen ejecutivo del sistema
│   ├── DEPLOYMENT_GUIDE.md           # Opciones de despliegue a producción
│   ├── QUICKSTART.md                 # Setup inicial en 5 minutos
│   ├── SETUP_CLOUD_SYNC.md           # Guía paso a paso para sincronización
│   ├── CAMBIOS_REPLICACION.md        # Resumen de cambios técnicos
│   ├── SOLUCION_ERROR_SYNC.md        # Solución al primer error de sync
│   └── SOLUCION_DATABASE_LOCKED.md   # Solución al error "database is locked"
│
├── .env.example                      # Template de variables de entorno
├── .env                              # Variables de entorno (no commitar)
├── tapandtoast.db                    # Base de datos SQLite local
└── tapandtoast.db-journal            # Archivo de journal de SQLite (auto-generado)
```

### 🗂️ Descripción de Archivos Clave

#### Configuración y Base de Datos
- **`database.py`**: Sistema dual de base de datos con:
  - SQLite local para desarrollo rápido
  - PostgreSQL en Railway para backup automático
  - Cola asíncrona con reintentos inteligentes
  - Detección automática de conexión a internet
  - Threading para evitar bloqueos

- **`models.py`**: Define todas las entidades:
  - Usuario, Producto, TipoProducto
  - Compra, DetalleCompra, QR
  - EncuestaSeatDelivery
  - Usa enums para estados

- **`schemas.py`**: Validación Pydantic v2 con:
  - Request/Response schemas
  - Computed fields para cálculos
  - Validación de enums y tipos

#### Routers (Endpoints)
- **`usuario.py`**: Autenticación, registro, perfil, saldo
- **`producto.py`**: Menú, categorías, búsqueda
- **`compra.py`**: Órdenes, historial, QR, estados
- **`analytics.py`**: Reportes, análisis de compras
- **`conversion.py`**: Conversión de monedas
- **`admin.py`**: Monitoreo, sincronización, salud del sistema

#### Scripts Utilitarios
- **`run_server.py`**: Inicia servidor con auto-reload
- **`seed_data.py`**: Carga datos de prueba
- **`sync_to_cloud.py`**: Sincronización manual completa
- **`check_users.py`**: Verifica estado de sincronización
- **`watch_sync_status.py`**: Monitor en tiempo real
- **`test_offline_sync.py`**: Simula modo offline
- **`test_sync.py`**: Tests automatizados

#### Documentación
La documentación está dividida por tema:
- **Guías de inicio**: QUICKSTART.md, GUIA_RAPIDA.md
- **Configuración**: SETUP_CLOUD_SYNC.md, CONFIGURACION_COMPLETADA.md
- **Sistema de sincronización**: SINCRONIZACION_OFFLINE.md, CAMBIOS_REPLICACION.md
- **Soluciones**: SOLUCION_ERROR_SYNC.md, SOLUCION_DATABASE_LOCKED.md
- **Despliegue**: DEPLOYMENT_GUIDE.md
- **API**: API_DOCUMENTATION.md, .github/copilot-instructions.md
```

## 🚀 Instalación y Configuración

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
# Por defecto usa solo SQLite local
```

5. **Poblar la base de datos con datos de prueba**
```bash
python seed_data.py
```

6. **Ejecutar el servidor**
```bash
python run_server.py
```

El servidor estará disponible en `http://localhost:8080`

### ☁️ Replicación a la Nube (Opcional)

Para configurar replicación automática a PostgreSQL en la nube:

1. **Crear base de datos PostgreSQL** en Railway, Neon o Render (ver [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))
2. **Configurar `.env`**:
```env
DATABASE_MODE=local
CLOUD_DATABASE_URL=postgresql://user:password@host:port/database
AUTO_SYNC_TO_CLOUD=true
```
3. **Sincronización inicial**:
```bash
python sync_to_cloud.py
```

Ahora cada cambio en tu base de datos local se replicará automáticamente a la nube. Ver la [Guía de Despliegue](DEPLOYMENT_GUIDE.md) para más detalles.

## � Sistema de Sincronización Offline

El backend implementa un sistema robusto de sincronización asíncrona que funciona incluso sin conexión a internet:

### ✨ Características
- **Sincronización automática**: Cada cambio se replica a Railway automáticamente
- **Modo offline**: Si no hay internet, los cambios se guardan en una cola en memoria
- **Reintentos inteligentes**: Cada 30 segundos intenta reconectar
- **Sin bloqueos**: Usa threading para no bloquear operaciones
- **Monitoreo**: Endpoint `/admin/sync-status` para ver el estado

### 📊 Cómo Funciona

**Con internet:**
```
Usuario → SQLite Local (instantáneo)
       ↓
    201 OK al cliente
       ↓
  Cola de sincronización
       ↓
Thread procesa → Railway PostgreSQL ✅
```
**Tiempo**: ~200ms

**Sin internet:**
```
Usuario → SQLite Local (instantáneo)
       ↓
    201 OK al cliente
       ↓
  Operación en cola (en memoria)
       ↓
Sistema detecta sin internet
       ↓
Espera 30s y reintenta
       ↓
Cuando vuelve internet → Sincroniza ✅
```

### 🧪 Verificar Sincronización

```bash
# Ver estado actual
python check_users.py

# Monitor en tiempo real
python watch_sync_status.py

# Endpoint de API
curl http://localhost:8080/admin/sync-status
```

### 🔧 Configuración

En `database.py` puedes ajustar:
```python
RETRY_DELAY_NO_INTERNET = 30  # Segundos entre intentos
MAX_RETRIES = 5               # Máximo de reintentos
INTERNET_CHECK_CACHE = 10     # Cache de detección (segundos)
```

## 📖 Documentación de la API

Una vez el servidor esté ejecutándose, puedes acceder a:

- **Documentación interactiva (Swagger)**: `http://localhost:8080/docs`
- **Documentación alternativa (ReDoc)**: `http://localhost:8080/redoc`

## �️ Scripts Disponibles

### Desarrollo
```bash
# Iniciar servidor con auto-reload
python run_server.py

# Poblar base de datos con datos de prueba
python seed_data.py
```

### Sincronización
```bash
# Verificar estado de sincronización
python check_users.py

# Sincronización manual completa
python sync_to_cloud.py

# Monitor en tiempo real
python watch_sync_status.py

# Test de sincronización offline
python test_offline_sync.py

# Tests automatizados
python test_sync.py
```

### Análisis
```bash
# Exportar análisis de tiempos de compras
python scripts/export_compras_tiempos.py
```

---

La API usa JWT (JSON Web Tokens) para autenticación. Para acceder a endpoints protegidos:

1. **Registrar un usuario**: `POST /usuarios/`
2. **Obtener token**: `POST /usuarios/token`
3. **Usar el token** en el header: `Authorization: Bearer <token>`

### Usuario de Prueba
- **Email**: `juan@test.com`
- **Contraseña**: `123456`
- **Saldo inicial**: $50,000

## 🛍️ Flujo de Compra

1. **Ver menú**: `GET /productos/`
2. **Crear compra**: `POST /compras/` (con lista de productos)
3. **Obtener QR**: Se genera automáticamente con la compra
4. **Seguimiento**: El staff actualiza el estado de la orden
5. **Entrega**: Escaneo del QR para completar la entrega

## 📊 Modelo de Datos

### Entidades Principales

- **Usuario**: Clientes del bar con saldo digital
- **TipoProducto**: Categorías del menú (Cervezas, Cócteles, etc.)
- **Producto**: Items del menú con precio y disponibilidad
- **Compra**: Órdenes de los usuarios
- **DetalleCompra**: Productos específicos dentro de una compra
- **QR**: Códigos únicos para validar entregas

### Estados de Compra
- `CARRITO`: En proceso de creación
- `PAGADO`: Pagada, esperando preparación
- `EN_PREPARACION`: Siendo preparada por el staff
- `LISTO`: Lista para recoger
- `ENTREGADO`: Entregada al cliente

## 🔧 Endpoints Principales

### Usuarios
- `POST /usuarios/` - Registro
- `POST /usuarios/token` - Login
- `GET /usuarios/me` - Perfil del usuario
- `POST /usuarios/me/recargar` - Recargar saldo

### Productos
- `GET /productos/` - Listar menú
- `GET /productos/{id}` - Detalle de producto
- `POST /productos/` - Crear producto (Admin)

### Compras
- `POST /compras/` - Crear nueva compra
- `GET /compras/me` - Historial de compras
- `GET /compras/pendientes` - Órdenes pendientes (Staff)
- `PUT /compras/{id}/estado` - Actualizar estado (Staff)
- `POST /compras/qr/escanear` - Escanear QR para entrega (Staff)

## � Troubleshooting

### Error: "database is locked"
```bash
# Detener servidor (Ctrl+C)
rm -f tapandtoast.db-journal
python run_server.py
```

### Usuarios no se sincronizan
```bash
# 1. Verificar estado
curl http://localhost:8080/admin/sync-status

# 2. Ver cola de sincronización
python watch_sync_status.py

# 3. Sincronizar manualmente
python sync_to_cloud.py
```

### Sin conexión a internet (esperado)
El sistema intentará reconectar cada 30 segundos. Los cambios se guardan localmente en la cola.

### Error de bcrypt
Ya está solucionado - las contraseñas se truncan automáticamente a 72 bytes (límite de bcrypt).

---

Para producción, considera:

1. **Cambiar la base de datos** a PostgreSQL en `database.py`
2. **Configurar variables de entorno** para la clave secreta JWT
3. **Usar un servidor ASGI** como Gunicorn con workers de Uvicorn
4. **Configurar HTTPS** y certificados SSL
5. **Implementar logging** y monitoreo

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## � Recursos Documentación

Guías de inicio rápido:
- [QUICKSTART.md](QUICKSTART.md) - Setup inicial en 5 minutos
- [GUIA_RAPIDA.md](GUIA_RAPIDA.md) - Comandos más comunes

Configuración y sincronización:
- [SETUP_CLOUD_SYNC.md](SETUP_CLOUD_SYNC.md) - Paso a paso para sincronización
- [SINCRONIZACION_OFFLINE.md](SINCRONIZACION_OFFLINE.md) - Sistema de sync offline
- [CONFIGURACION_COMPLETADA.md](CONFIGURACION_COMPLETADA.md) - Estado actual

Soluciones a problemas:
- [SOLUCION_ERROR_SYNC.md](SOLUCION_ERROR_SYNC.md) - Error de sincronización
- [SOLUCION_DATABASE_LOCKED.md](SOLUCION_DATABASE_LOCKED.md) - Error "database is locked"

Despliegue y arquitectura:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Opciones de producción
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Endpoints completos
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Para AI agents

## 🌐 Variables de Entorno

```env
# Base de datos
DATABASE_MODE=local                    # local o cloud
CLOUD_DATABASE_URL=postgresql://...    # URL de PostgreSQL (opcional)
AUTO_SYNC_TO_CLOUD=true               # Habilitar sincronización

# Seguridad
SECRET_KEY=your-secret-key            # Clave secreta para JWT
ALGORITHM=HS256                        # Algoritmo JWT

# Servidor
SERVER_HOST=0.0.0.0                   # Host del servidor
SERVER_PORT=8080                       # Puerto del servidor
```

## 🚀 Inicios Rápidos

### Modo Desarrollo Local (Sin Nube)
```bash
# Usar valores por defecto
python run_server.py
```

### Con Sincronización a Nube
```bash
# Configurar .env primero
# DATABASE_MODE=local
# CLOUD_DATABASE_URL=postgresql://...
# AUTO_SYNC_TO_CLOUD=true

python run_server.py
python watch_sync_status.py  # En otra terminal
```

### Monitoreo
```bash
# Terminal 1: Servidor
python run_server.py

# Terminal 2: Monitor en tiempo real
python watch_sync_status.py

# Terminal 3: Tests (opcional)
python test_sync.py
```

## 🎯 Arquitectura

```
┌─────────────────────────────────────────────┐
│        Aplicación Móvil (Flutter)          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      FastAPI Backend (Puerto 8080)         │
│  ├─ JWT Authentication                     │
│  ├─ Endpoints RESTful                      │
│  └─ Queue-based Sync System               │
└──────────┬──────────────────────┬──────────┘
           │                      │
           ▼                      ▼
    ┌────────────────┐   ┌─────────────────┐
    │  SQLite Local  │   │  PostgreSQL     │
    │ (tapandtoast   │   │  Railway (Nube) │
    │    .db)        │   │   (Backup)      │
    └────────────────┘   └─────────────────┘
           │                      ▲
           └──────────────────────┘
           Sincronización Async
           con Reintentos
```

## 📊 Estadísticas del Proyecto

- **Modelos**: 7 (Usuario, Producto, TipoProducto, Compra, DetalleCompra, QR, EncuestaSeatDelivery)
- **Routers**: 6 (usuario, producto, compra, analytics, conversion, admin)
- **Endpoints**: 20+
- **Scripts**: 7
- **Documentación**: 12 archivos
- **Líneas de código**: ~2000+

## �📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**TapAndToast** - Revolucionando la experiencia en bares, un tap a la vez! 🍻📱

### Stack Técnico
- FastAPI + Pydantic v2 + SQLAlchemy 2.0
- SQLite + PostgreSQL
- JWT + Bcrypt
- Threading + Queue (async sync)
- Railway (hosting nube)
- CORS habilitado para desarrollo

### Última Actualización
- Sistema de sincronización offline completo
- Manejo robusto de errores
- Monitoreo en tiempo real
- Documentación exhaustiva