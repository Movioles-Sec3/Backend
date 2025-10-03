# 📱 TapAndToast API - Documentación de Endpoints

## Información General

**Versión:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Documentación Interactiva:** `/docs` (Swagger UI)

## Índice

- [Autenticación](#autenticación)
- [Endpoints Generales](#endpoints-generales)
- [Usuarios](#usuarios)
- [Productos](#productos)
- [Compras](#compras)
- [Modelos de Datos](#modelos-de-datos)
- [Códigos de Estado](#códigos-de-estado)

---

## Autenticación

La API utiliza autenticación JWT (JSON Web Tokens) mediante el esquema Bearer.

### Cómo autenticarse:

1. Obtén un token mediante el endpoint `POST /usuarios/token`
2. Incluye el token en el header de las peticiones protegidas:
   ```
   Authorization: Bearer <tu_token_aquí>
   ```

**Duración del token:** 120 minutos (2 horas)

---

## Endpoints Generales

### 🏠 Root - Bienvenida

**Endpoint:** `GET /`

**Descripción:** Endpoint de bienvenida y verificación básica de la API.

**Autenticación:** No requerida

**Respuesta exitosa (200):**
```json
{
  "mensaje": "¡Bienvenido a TapAndToast API!",
  "version": "1.0.0",
  "documentacion": "/docs"
}
```

---

### ❤️ Health Check - Verificación de salud

**Endpoint:** `GET /health`

**Descripción:** Verifica que el servidor está funcionando correctamente.

**Autenticación:** No requerida

**Respuesta exitosa (200):**
```json
{
  "status": "ok",
  "mensaje": "El servidor está funcionando correctamente"
}
```

---

## Usuarios

### 📝 Crear Usuario (Registro)

**Endpoint:** `POST /usuarios/`

**Descripción:** Registra un nuevo usuario en el sistema.

**Autenticación:** No requerida

**Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "password": "password123"
}
```

**Respuesta exitosa (201):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "saldo": 0.0
}
```

**Errores posibles:**
- **400 Bad Request:** El email ya está registrado
- **422 Unprocessable Entity:** Datos inválidos (ej: email mal formado)

---

### 🔐 Login - Obtener Token

**Endpoint:** `POST /usuarios/token`

**Descripción:** Autentica un usuario y devuelve un token JWT.

**Autenticación:** No requerida

**Body:**
```json
{
  "email": "juan@example.com",
  "password": "password123"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errores posibles:**
- **401 Unauthorized:** Email o contraseña incorrectos

---

### 👤 Obtener Perfil del Usuario

**Endpoint:** `GET /usuarios/me`

**Descripción:** Obtiene la información del usuario autenticado actualmente.

**Autenticación:** ✅ Requerida (Bearer Token)

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "saldo": 50000.0
}
```

**Errores posibles:**
- **401 Unauthorized:** Token inválido o expirado

---

### 💰 Recargar Saldo

**Endpoint:** `POST /usuarios/me/recargar`

**Descripción:** Añade saldo al monedero del usuario autenticado.

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:**
```json
{
  "monto": 50000.0
}
```

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "saldo": 100000.0
}
```

**Errores posibles:**
- **400 Bad Request:** El monto debe ser mayor a 0
- **401 Unauthorized:** Token inválido o expirado

---

## Productos

### 📋 Listar Productos

**Endpoint:** `GET /productos/`

**Descripción:** Obtiene la lista de productos (menú). Permite filtrar por tipo y disponibilidad.

**Autenticación:** No requerida

**Query Parameters:**
- `id_tipo` (opcional): Filtrar por tipo de producto (int)
- `disponible` (opcional, default=true): Mostrar solo productos disponibles (bool)

**Ejemplos:**
- `/productos/` - Todos los productos disponibles
- `/productos/?id_tipo=1` - Productos del tipo 1 (ej: Bebidas)
- `/productos/?disponible=false` - Productos no disponibles

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "nombre": "Cerveza Artesanal IPA",
    "descripcion": "Cerveza con notas cítricas y amargor equilibrado",
    "imagen_url": "https://example.com/cerveza-ipa.jpg",
    "precio": 8500.0,
    "disponible": true,
    "id_tipo": 1,
    "tipo_producto": {
      "id": 1,
      "nombre": "Bebidas Alcohólicas"
    }
  },
  {
    "id": 2,
    "nombre": "Hamburguesa Clásica",
    "descripcion": "Hamburguesa de carne con queso, lechuga y tomate",
    "imagen_url": "https://example.com/hamburguesa.jpg",
    "precio": 15000.0,
    "disponible": true,
    "id_tipo": 2,
    "tipo_producto": {
      "id": 2,
      "nombre": "Comida"
    }
  }
]
```

---

### 🔍 Obtener Producto por ID

**Endpoint:** `GET /productos/{producto_id}`

**Descripción:** Obtiene los detalles de un producto específico.

**Autenticación:** No requerida

**Path Parameters:**
- `producto_id`: ID del producto (int)

**Ejemplo:** `/productos/1`

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Cerveza Artesanal IPA",
  "descripcion": "Cerveza con notas cítricas y amargor equilibrado",
  "imagen_url": "https://example.com/cerveza-ipa.jpg",
  "precio": 8500.0,
  "disponible": true,
  "id_tipo": 1,
  "tipo_producto": {
    "id": 1,
    "nombre": "Bebidas Alcohólicas"
  }
}
```

**Errores posibles:**
- **404 Not Found:** Producto no encontrado

---

### 🏷️ Listar Tipos de Producto

**Endpoint:** `GET /productos/tipos/`

**Descripción:** Obtiene todas las categorías de productos disponibles.

**Autenticación:** No requerida

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "nombre": "Bebidas Alcohólicas"
  },
  {
    "id": 2,
    "nombre": "Comida"
  },
  {
    "id": 3,
    "nombre": "Bebidas Sin Alcohol"
  },
  {
    "id": 4,
    "nombre": "Postres"
  }
]
```

---

### ➕ Crear Tipo de Producto (Admin)

**Endpoint:** `POST /productos/tipos/`

**Descripción:** Crea una nueva categoría de productos.

**Autenticación:** No requerida (⚠️ En producción debe protegerse con autenticación de administrador)

**Body:**
```json
{
  "nombre": "Cócteles"
}
```

**Respuesta exitosa (201):**
```json
{
  "id": 5,
  "nombre": "Cócteles"
}
```

**Errores posibles:**
- **400 Bad Request:** El tipo de producto ya existe

---

### ➕ Crear Producto (Admin)

**Endpoint:** `POST /productos/`

**Descripción:** Crea un nuevo producto en el menú.

**Autenticación:** No requerida (⚠️ En producción debe protegerse con autenticación de administrador)

**Body:**
```json
{
  "nombre": "Mojito",
  "descripcion": "Cóctel refrescante de ron, menta y lima",
  "imagen_url": "https://example.com/mojito.jpg",
  "precio": 12000.0,
  "disponible": true,
  "id_tipo": 5
}
```

**Respuesta exitosa (201):**
```json
{
  "id": 10,
  "nombre": "Mojito",
  "descripcion": "Cóctel refrescante de ron, menta y lima",
  "imagen_url": "https://example.com/mojito.jpg",
  "precio": 12000.0,
  "disponible": true,
  "id_tipo": 5,
  "tipo_producto": {
    "id": 5,
    "nombre": "Cócteles"
  }
}
```

**Errores posibles:**
- **400 Bad Request:** El tipo de producto no existe

---

### ✏️ Actualizar Producto (Admin)

**Endpoint:** `PUT /productos/{producto_id}`

**Descripción:** Actualiza la información de un producto existente.

**Autenticación:** No requerida (⚠️ En producción debe protegerse con autenticación de administrador)

**Path Parameters:**
- `producto_id`: ID del producto a actualizar (int)

**Body:**
```json
{
  "nombre": "Mojito Premium",
  "descripcion": "Cóctel refrescante de ron premium, menta fresca y lima",
  "imagen_url": "https://example.com/mojito-premium.jpg",
  "precio": 15000.0,
  "disponible": true,
  "id_tipo": 5
}
```

**Respuesta exitosa (200):**
```json
{
  "id": 10,
  "nombre": "Mojito Premium",
  "descripcion": "Cóctel refrescante de ron premium, menta fresca y lima",
  "imagen_url": "https://example.com/mojito-premium.jpg",
  "precio": 15000.0,
  "disponible": true,
  "id_tipo": 5,
  "tipo_producto": {
    "id": 5,
    "nombre": "Cócteles"
  }
}
```

**Errores posibles:**
- **404 Not Found:** Producto no encontrado
- **400 Bad Request:** El tipo de producto no existe

---

## Compras

### 🛒 Crear Compra (Realizar Pedido)

**Endpoint:** `POST /compras/`

**Descripción:** Endpoint principal de negocio. Crea una nueva compra, procesa el pago descontando del saldo del usuario y genera un código QR para recoger la orden.

**Autenticación:** ✅ Requerida (Bearer Token)

**Flujo:**
1. Valida que los productos existan y estén disponibles
2. Calcula el total de la compra
3. Verifica que el usuario tenga saldo suficiente
4. Descuenta el saldo del usuario
5. Crea la compra con estado `PAGADO`
6. Genera un código QR único para la orden
7. Retorna los detalles de la compra incluyendo el QR

**Body:**
```json
{
  "productos": [
    {
      "id_producto": 1,
      "cantidad": 2
    },
    {
      "id_producto": 3,
      "cantidad": 1
    }
  ]
}
```

**Respuesta exitosa (201):**
```json
{
  "id": 15,
  "fecha_hora": "2025-10-03T14:30:00",
  "total": 32000.0,
  "estado": "PAGADO",
  "detalles": [
    {
      "id_producto": 1,
      "cantidad": 2,
      "precio_unitario_compra": 8500.0,
      "producto": {
        "id": 1,
        "nombre": "Cerveza Artesanal IPA",
        "descripcion": "Cerveza con notas cítricas y amargor equilibrado",
        "imagen_url": "https://example.com/cerveza-ipa.jpg",
        "precio": 8500.0,
        "disponible": true,
        "id_tipo": 1,
        "tipo_producto": {
          "id": 1,
          "nombre": "Bebidas Alcohólicas"
        }
      }
    },
    {
      "id_producto": 3,
      "cantidad": 1,
      "precio_unitario_compra": 15000.0,
      "producto": {
        "id": 3,
        "nombre": "Hamburguesa Clásica",
        "descripcion": "Hamburguesa de carne con queso",
        "imagen_url": "https://example.com/hamburguesa.jpg",
        "precio": 15000.0,
        "disponible": true,
        "id_tipo": 2,
        "tipo_producto": {
          "id": 2,
          "nombre": "Comida"
        }
      }
    }
  ],
  "qr": {
    "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
    "estado": "ACTIVO"
  }
}
```

**Errores posibles:**
- **400 Bad Request:** 
  - La compra debe tener al menos un producto
  - La cantidad debe ser mayor a 0
  - Saldo insuficiente
  - Producto no disponible
- **404 Not Found:** Producto no encontrado
- **401 Unauthorized:** Token inválido o expirado
- **500 Internal Server Error:** Error al procesar la compra

---

### 📜 Historial de Compras

**Endpoint:** `GET /compras/me`

**Descripción:** Obtiene el historial de compras del usuario autenticado (excluye carritos).

**Autenticación:** ✅ Requerida (Bearer Token)

**Respuesta exitosa (200):**
```json
[
  {
    "id": 14,
    "fecha_hora": "2025-10-02T18:45:00",
    "total": 23500.0,
    "estado": "ENTREGADO",
    "detalles": [
      {
        "id_producto": 1,
        "cantidad": 1,
        "precio_unitario_compra": 8500.0,
        "producto": {
          "id": 1,
          "nombre": "Cerveza Artesanal IPA",
          "descripcion": "Cerveza con notas cítricas",
          "imagen_url": "https://example.com/cerveza-ipa.jpg",
          "precio": 8500.0,
          "disponible": true,
          "id_tipo": 1,
          "tipo_producto": {
            "id": 1,
            "nombre": "Bebidas Alcohólicas"
          }
        }
      }
    ],
    "qr": {
      "codigo_qr_hash": "b4e9d3f2a1c5e8f7b6a9d0c1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1",
      "estado": "CANJEADO"
    }
  },
  {
    "id": 15,
    "fecha_hora": "2025-10-03T14:30:00",
    "total": 32000.0,
    "estado": "LISTO",
    "detalles": [...],
    "qr": {
      "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
      "estado": "ACTIVO"
    }
  }
]
```

**Errores posibles:**
- **401 Unauthorized:** Token inválido o expirado

---

### 📋 Listar Compras Pendientes (Staff)

**Endpoint:** `GET /compras/pendientes`

**Descripción:** Lista todas las compras con estado `PAGADO` o `EN_PREPARACION` para que el staff las procese.

**Autenticación:** No requerida (⚠️ En producción debe protegerse con autenticación de staff)

**Respuesta exitosa (200):**
```json
[
  {
    "id": 15,
    "fecha_hora": "2025-10-03T14:30:00",
    "total": 32000.0,
    "estado": "PAGADO",
    "detalles": [...],
    "qr": {
      "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
      "estado": "ACTIVO"
    }
  },
  {
    "id": 16,
    "fecha_hora": "2025-10-03T14:35:00",
    "total": 18000.0,
    "estado": "EN_PREPARACION",
    "detalles": [...],
    "qr": {
      "codigo_qr_hash": "c5f0d4a3b2e6f9a8c7d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
      "estado": "ACTIVO"
    }
  }
]
```

---

### 🔄 Actualizar Estado de Compra (Staff)

**Endpoint:** `PUT /compras/{compra_id}/estado`

**Descripción:** Actualiza el estado de una compra. Solo se permiten transiciones válidas.

**Autenticación:** No requerida (⚠️ En producción debe protegerse con autenticación de staff)

**Path Parameters:**
- `compra_id`: ID de la compra (int)

**Body:**
```json
{
  "estado": "EN_PREPARACION"
}
```

**Estados de Compra:**
- `CARRITO`: Estado inicial (no usado en este flujo)
- `PAGADO`: Compra pagada, esperando preparación
- `EN_PREPARACION`: Orden en preparación
- `LISTO`: Orden lista para recoger
- `ENTREGADO`: Orden entregada al cliente

**Transiciones Válidas:**
- `PAGADO` → `EN_PREPARACION`
- `EN_PREPARACION` → `LISTO`
- `LISTO` → `ENTREGADO`

**Respuesta exitosa (200):**
```json
{
  "id": 15,
  "fecha_hora": "2025-10-03T14:30:00",
  "total": 32000.0,
  "estado": "EN_PREPARACION",
  "detalles": [...],
  "qr": {
    "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
    "estado": "ACTIVO"
  }
}
```

**Errores posibles:**
- **404 Not Found:** Compra no encontrada
- **400 Bad Request:** Transición de estado inválida (ej: no se puede cambiar de `PAGADO` a `ENTREGADO` directamente)

---

### 📱 Escanear QR (Staff)

**Endpoint:** `POST /compras/qr/escanear`

**Descripción:** Verifica un código QR y procesa la entrega de la orden. Marca el QR como canjeado y la compra como entregada.

**Autenticación:** No requerida (⚠️ En producción debe protegerse con autenticación de staff)

**Validaciones:**
- El código QR debe existir
- El QR debe estar en estado `ACTIVO`
- La compra debe estar en estado `LISTO`

**Body:**
```json
{
  "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2"
}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Orden entregada exitosamente",
  "compra_id": 15,
  "cliente": "Juan Pérez",
  "total": 32000.0
}
```

**Efectos:**
- QR cambia a estado `CANJEADO`
- Compra cambia a estado `ENTREGADO`

**Errores posibles:**
- **404 Not Found:** Código QR no válido
- **400 Bad Request:** 
  - El código QR ya fue canjeado/expirado
  - La orden no está lista para entregar (debe estar en estado `LISTO`)

---

## Modelos de Datos

### Usuario

```json
{
  "id": "integer",
  "nombre": "string",
  "email": "string (formato email)",
  "saldo": "float"
}
```

---

### TipoProducto

```json
{
  "id": "integer",
  "nombre": "string"
}
```

---

### Producto

```json
{
  "id": "integer",
  "nombre": "string",
  "descripcion": "string | null",
  "imagen_url": "string | null",
  "precio": "float",
  "disponible": "boolean",
  "id_tipo": "integer",
  "tipo_producto": "TipoProducto"
}
```

---

### DetalleCompra

```json
{
  "id_producto": "integer",
  "cantidad": "integer",
  "precio_unitario_compra": "float",
  "producto": "Producto"
}
```

---

### Compra

```json
{
  "id": "integer",
  "fecha_hora": "datetime (ISO 8601)",
  "total": "float",
  "estado": "EstadoCompra",
  "detalles": "DetalleCompra[]",
  "qr": "QR | null"
}
```

---

### QR

```json
{
  "codigo_qr_hash": "string (SHA-256 hash)",
  "estado": "EstadoQR"
}
```

---

### Token

```json
{
  "access_token": "string (JWT)",
  "token_type": "string (bearer)"
}
```

---

## Códigos de Estado

### Códigos de Éxito

- **200 OK:** Solicitud exitosa
- **201 Created:** Recurso creado exitosamente

### Códigos de Error del Cliente

- **400 Bad Request:** La solicitud contiene datos inválidos
- **401 Unauthorized:** Autenticación fallida o token inválido
- **404 Not Found:** Recurso no encontrado
- **422 Unprocessable Entity:** Datos con formato incorrecto

### Códigos de Error del Servidor

- **500 Internal Server Error:** Error interno del servidor

---

## Enumeraciones

### EstadoCompra

```python
CARRITO = "CARRITO"          # Compra en proceso (no usado actualmente)
PAGADO = "PAGADO"            # Compra pagada, esperando preparación
EN_PREPARACION = "EN_PREPARACION"  # Orden en preparación
LISTO = "LISTO"              # Orden lista para recoger
ENTREGADO = "ENTREGADO"      # Orden entregada al cliente
```

### EstadoQR

```python
ACTIVO = "ACTIVO"        # QR válido, puede ser canjeado
CANJEADO = "CANJEADO"    # QR ya fue usado
EXPIRADO = "EXPIRADO"    # QR expirado (no implementado aún)
```

---

## Ejemplos de Flujo Completo

### Flujo 1: Usuario Realiza un Pedido

1. **Registro:** `POST /usuarios/` con datos del usuario
2. **Login:** `POST /usuarios/token` para obtener el token JWT
3. **Recargar saldo:** `POST /usuarios/me/recargar` con el monto deseado
4. **Ver menú:** `GET /productos/` para ver los productos disponibles
5. **Crear compra:** `POST /compras/` con la lista de productos
6. **Resultado:** Se recibe la compra con el código QR generado

### Flujo 2: Staff Procesa y Entrega un Pedido

1. **Ver órdenes pendientes:** `GET /compras/pendientes`
2. **Iniciar preparación:** `PUT /compras/{id}/estado` con estado `EN_PREPARACION`
3. **Marcar como lista:** `PUT /compras/{id}/estado` con estado `LISTO`
4. **Cliente presenta QR:** Staff escanea el código
5. **Entregar orden:** `POST /compras/qr/escanear` con el código QR
6. **Resultado:** Orden marcada como entregada

---

## Notas Importantes

### Seguridad

- ⚠️ Los endpoints marcados como **(Admin)** y **(Staff)** actualmente **NO tienen autenticación implementada**. En producción deben protegerse con roles de usuario.
- 🔒 La clave secreta JWT está hardcodeada en el código. **Debe cambiarse en producción** usando variables de entorno.
- 🌐 CORS está configurado para aceptar todos los orígenes (`*`). En producción debe restringirse a dominios específicos.

### Base de Datos

- El sistema usa SQLite (`tapandtoast.db`) por defecto
- Las tablas se crean automáticamente al iniciar la aplicación
- Se incluye un script de seed (`seed_data.py`) para poblar datos de prueba

### Precios

- Todos los precios se manejan como valores flotantes (float)
- Se recomienda usar un sistema de monedas con precisión decimal en producción

### QR Codes

- Los códigos QR se generan como hashes SHA-256 de UUIDs
- Son únicos y no reversibles
- En una implementación real, podrían incluir información adicional o usar un formato específico para apps de generación de QR

---

## Documentación Interactiva

Para explorar y probar todos los endpoints de forma interactiva, visita:

**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

Estas interfaces permiten:
- Ver todos los endpoints disponibles
- Probar las peticiones directamente desde el navegador
- Ver los esquemas de datos detallados
- Autenticarse con tokens JWT

---

## Soporte

Para más información sobre la implementación, consulta:
- `README.md` - Guía de instalación y configuración
- `models.py` - Modelos de base de datos
- `schemas.py` - Esquemas de validación Pydantic
- `/docs` - Documentación interactiva de Swagger

