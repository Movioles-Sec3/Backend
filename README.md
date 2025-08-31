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
- **SQLite**: Base de datos para desarrollo (fácil migración a PostgreSQL)
- **JWT**: Autenticación segura con tokens
- **Pydantic**: Validación de datos automática
- **Bcrypt**: Hash seguro de contraseñas

## 📁 Estructura del Proyecto

```
Backend/
├── main.py              # Aplicación principal FastAPI
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
├── auth.py              # Sistema de autenticación JWT
├── dependencies.py      # Dependencias reutilizables
├── seed_data.py         # Script para datos de prueba
├── run_server.py        # Script para ejecutar el servidor
├── requirements.txt     # Dependencias Python
└── routers/
    ├── usuario.py       # Endpoints de usuarios
    ├── producto.py      # Endpoints de productos/menú
    └── compra.py        # Endpoints de compras y QR
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

4. **Poblar la base de datos con datos de prueba**
```bash
python seed_data.py
```

5. **Ejecutar el servidor**
```bash
python run_server.py
```

El servidor estará disponible en `http://localhost:8000`

## 📖 Documentación de la API

Una vez el servidor esté ejecutándose, puedes acceder a:

- **Documentación interactiva (Swagger)**: `http://localhost:8000/docs`
- **Documentación alternativa (ReDoc)**: `http://localhost:8000/redoc`

## 🔐 Autenticación

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

## 🚀 Despliegue en Producción

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

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**TapAndToast** - Revolucionando la experiencia en bares, un tap a la vez! 🍻📱