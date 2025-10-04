# 📱 TapAndToast API - Documentación de Endpoints

## Información General

**Versión:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Documentación Interactiva:** `/docs` (Swagger UI)

## Índice

- [Resumen de Endpoints](#resumen-de-endpoints)
- [Autenticación](#autenticación)
- [Endpoints Generales](#endpoints-generales)
- [Usuarios](#usuarios)
- [Productos](#productos)
- [Compras](#compras)
- [Analytics](#analytics)
- [Modelos de Datos](#modelos-de-datos)
- [Códigos de Estado](#códigos-de-estado)
- [Medición de Tiempos en Compras](#-medición-de-tiempos-en-compras)
- [Ejemplos de Flujo Completo](#ejemplos-de-flujo-completo)

---

## Resumen de Endpoints

### Tabla de Endpoints Disponibles (16 total)

| Método | Endpoint | Descripción | Auth Requerida |
|--------|----------|-------------|----------------|
| **GENERALES** | | | |
| GET | `/` | Bienvenida a la API | ❌ |
| GET | `/health` | Verificación de salud | ❌ |
| **USUARIOS** | | | |
| POST | `/usuarios/` | Registro de usuario | ❌ |
| POST | `/usuarios/token` | Login (obtener token JWT) | ❌ |
| GET | `/usuarios/me` | Obtener perfil del usuario actual | ✅ |
| POST | `/usuarios/me/recargar` | Recargar saldo del usuario | ✅ |
| **PRODUCTOS** | | | |
| GET | `/productos/` | Listar productos (filtrar por categoría) | ❌ |
| GET | `/productos/{producto_id}` | Obtener producto específico | ❌ |
| GET | `/productos/tipos/` | Listar categorías/tipos de producto | ❌ |
| GET | `/productos/recomendados` | Obtener productos recomendados (más vendidos) | ❌ |
| POST | `/productos/tipos/` | Crear nueva categoría (Admin) | ❌* |
| POST | `/productos/` | Crear nuevo producto (Admin) | ❌* |
| PUT | `/productos/{producto_id}` | Actualizar producto (Admin) | ❌* |
| **COMPRAS** | | | |
| POST | `/compras/` | Crear compra (realizar pedido) | ✅ |
| GET | `/compras/me` | Historial de compras del usuario | ✅ |
| GET | `/compras/pendientes` | Listar órdenes pendientes (Staff) | ❌* |
| PUT | `/compras/{compra_id}/estado` | Actualizar estado de compra (Staff) | ❌* |
| POST | `/compras/qr/escanear` | Escanear QR para entregar orden (Staff) | ❌* |
| **ANALYTICS** | | | |
| GET | `/analytics/reorders-by-category` | Reordenes por categoría y hora | ❌ |

**Nota:** Los endpoints marcados con ❌* deberían requerir autenticación de Admin/Staff en producción, pero actualmente son públicos.

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

> ⚠️ **Nota importante sobre el orden de los endpoints:**  
> En esta documentación, los endpoints están listados en el **orden correcto de implementación**. Las rutas específicas (como `/recomendados`, `/tipos/`) deben definirse ANTES que las rutas con parámetros dinámicos (como `/{producto_id}`) para evitar conflictos de routing en FastAPI.

### 📋 Listar Productos / Obtener Productos por Categoría

**Endpoint:** `GET /productos/`

**Descripción:** Obtiene la lista de productos (menú). Permite filtrar por categoría (tipo) y disponibilidad. **Este endpoint se usa tanto para listar todos los productos como para obtener productos de una categoría específica.**

**Autenticación:** No requerida

**Query Parameters:**
- `id_tipo` (opcional): Filtrar por tipo de producto / categoría (int). **Úsalo para obtener solo productos de una categoría específica**
- `disponible` (opcional, default=true): Mostrar solo productos disponibles (bool)

**Casos de uso:**
- **Listar todos los productos:** `/productos/`
- **Productos de una categoría específica:** `/productos/?id_tipo=1` (ej: solo Bebidas Alcohólicas)
- **Productos no disponibles:** `/productos/?disponible=false`
- **Productos de una categoría que no están disponibles:** `/productos/?id_tipo=2&disponible=false`

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

### ⭐ Obtener Productos Recomendados

**Endpoint:** `GET /productos/recomendados`

**Descripción:** Obtiene una lista de productos recomendados basados en popularidad (los más vendidos). Sistema simple de recomendación que funciona incluso con pocos datos. Útil para mostrar en la pantalla principal o sugerir productos a los clientes.

**Autenticación:** No requerida

**Query Parameters:**
- `limit` (opcional, default=5): Número de productos recomendados a retornar (int)
- `categoria_id` (opcional): Filtrar recomendaciones por categoría específica (int)

**Casos de uso:**
- **Top 5 productos más populares:** `/productos/recomendados`
- **Top 10 productos:** `/productos/recomendados?limit=10`
- **Top 5 bebidas más populares:** `/productos/recomendados?categoria_id=1`
- **Top 3 comidas:** `/productos/recomendados?limit=3&categoria_id=2`

**Respuesta exitosa (200):**
```json
[
  {
    "id": 2,
    "nombre": "Club Colombia",
    "descripcion": "Cerveza colombiana premium",
    "imagen_url": "https://example.com/club.jpg",
    "precio": 7000.0,
    "disponible": true,
    "id_tipo": 1,
    "tipo_producto": {
      "id": 1,
      "nombre": "Cervezas"
    }
  },
  {
    "id": 5,
    "nombre": "Nachos con Queso",
    "descripcion": "Nachos crujientes con queso cheddar fundido",
    "imagen_url": "https://example.com/nachos.jpg",
    "precio": 12000.0,
    "disponible": true,
    "id_tipo": 2,
    "tipo_producto": {
      "id": 2,
      "nombre": "Comida"
    }
  },
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
      "nombre": "Cervezas"
    }
  }
]
```

**Cómo funciona:**
- Cuenta cuántas veces se ha comprado cada producto (en `detalles_compra`)
- Ordena por cantidad de ventas de mayor a menor
- Retorna los productos más populares
- Si un producto nunca se ha vendido, aparecerá al final
- Solo muestra productos disponibles

**Nota:** Los productos se ordenan por popularidad (más vendidos primero). Si hay empate en ventas, se ordenan por ID. Funciona perfectamente incluso sin datos históricos de ventas.

---

### 🔍 Obtener Producto por ID

**Endpoint:** `GET /productos/{producto_id}`

**Descripción:** Obtiene los detalles de un producto específico por su ID.

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

**Nota:** ⚠️ Este endpoint debe estar definido DESPUÉS de las rutas específicas (`/recomendados`, `/tipos/`) para evitar conflictos de routing.

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
  },
  "fecha_en_preparacion": null,
  "fecha_listo": null,
  "fecha_entregado": null,
  "tiempo_hasta_preparacion": null,
  "tiempo_preparacion": null,
  "tiempo_espera_entrega": null,
  "tiempo_total": null
}
```

**Nota:** En una compra recién creada, todos los campos de timestamps y tiempos calculados son `null` porque aún no ha pasado por las etapas siguientes.

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
    "fecha_hora": "2025-10-04T18:45:00Z",
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
    },
    "fecha_en_preparacion": "2025-10-04T18:47:30Z",
    "fecha_listo": "2025-10-04T18:55:15Z",
    "fecha_entregado": "2025-10-04T19:02:45Z",
    "tiempo_hasta_preparacion": 150.0,
    "tiempo_preparacion": 465.0,
    "tiempo_espera_entrega": 450.0,
    "tiempo_total": 1065.0
  },
  {
    "id": 15,
    "fecha_hora": "2025-10-04T14:30:00Z",
    "total": 32000.0,
    "estado": "LISTO",
    "detalles": [...],
    "qr": {
      "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
      "estado": "ACTIVO"
    },
    "fecha_en_preparacion": "2025-10-04T14:32:00Z",
    "fecha_listo": "2025-10-04T14:45:00Z",
    "fecha_entregado": null,
    "tiempo_hasta_preparacion": 120.0,
    "tiempo_preparacion": 780.0,
    "tiempo_espera_entrega": null,
    "tiempo_total": null
  }
]
```

**Ejemplo de interpretación de tiempos (Compra #14):**
- ⏱️ **150 segundos** (2.5 min) - Tiempo hasta que el staff empezó a preparar
- ⏱️ **465 segundos** (7.75 min) - Duración de la preparación
- ⏱️ **450 segundos** (7.5 min) - Tiempo que el cliente tardó en recoger
- ⏱️ **1065 segundos** (17.75 min) - Tiempo total del proceso

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

**Descripción:** Actualiza el estado de una compra. Solo se permiten transiciones válidas. **Registra automáticamente el timestamp correspondiente** (`fecha_en_preparacion`, `fecha_listo` o `fecha_entregado`) según el nuevo estado.

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
  "fecha_hora": "2025-10-04T14:30:00Z",
  "total": 32000.0,
  "estado": "EN_PREPARACION",
  "detalles": [...],
  "qr": {
    "codigo_qr_hash": "a3f8c9d2e1b4f7a6c3d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
    "estado": "ACTIVO"
  },
  "fecha_en_preparacion": "2025-10-04T14:32:00Z",
  "fecha_listo": null,
  "fecha_entregado": null,
  "tiempo_hasta_preparacion": 120.0,
  "tiempo_preparacion": null,
  "tiempo_espera_entrega": null,
  "tiempo_total": null
}
```

**Nota:** Al cambiar el estado, se registra automáticamente el timestamp correspondiente y se calculan los tiempos disponibles hasta ese momento.

**Errores posibles:**
- **404 Not Found:** Compra no encontrada
- **400 Bad Request:** Transición de estado inválida (ej: no se puede cambiar de `PAGADO` a `ENTREGADO` directamente)

---

### 📱 Escanear QR (Staff)

**Endpoint:** `POST /compras/qr/escanear`

**Descripción:** Verifica un código QR y procesa la entrega de la orden. Marca el QR como canjeado, la compra como entregada y **registra el timestamp de entrega** (`fecha_entregado`).

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
## Analytics

### 📊 Reordenes por Categoría y Horas del Día

**Endpoint:** `GET /analytics/reorders-by-category`

**Descripción:** Identifica qué categorías de productos son más frecuentemente reordenadas durante eventos y en qué horas del día ocurren esos reordenes. Un "reorder" se define como una compra que incluye una categoría que el mismo usuario ya había comprado anteriormente (antes del periodo consultado o previamente dentro del periodo). Cada compra contribuye como máximo 1 por categoría, independientemente de cuántos productos de esa categoría incluya.

**Autenticación:** No requerida

**Query Parameters:**
- `start` (opcional, ISO-8601 UTC): Inicio del rango (incluyente). Por defecto, últimos 30 días.
- `end` (opcional, ISO-8601 UTC): Fin del rango (excluyente). Por defecto, ahora.
- `timezone_offset_minutes` (opcional, int, default=0): Offset de zona horaria del cliente en minutos (ej: `-300` para UTC-5). Se usa para agrupar por hora local.

**Respuesta (200):**
```json
{
  "start": "2025-09-04T00:00:00Z",
  "end": "2025-10-04T00:00:00Z",
  "timezone_offset_minutes": -300,
  "categories": [
    {
      "categoria_id": 2,
      "categoria_nombre": "Cócteles",
      "reorder_count": 18,
      "hour_distribution": [
        { "hour": 20, "count": 5 },
        { "hour": 21, "count": 7 },
        { "hour": 22, "count": 6 }
      ],
      "peak_hours": [21]
    },
    {
      "categoria_id": 1,
      "categoria_nombre": "Cervezas",
      "reorder_count": 12,
      "hour_distribution": [
        { "hour": 18, "count": 3 },
        { "hour": 19, "count": 3 },
        { "hour": 23, "count": 6 }
      ],
      "peak_hours": [23]
    }
  ]
}
```

**Notas:**
- Se consideran compras con estado `PAGADO`, `EN_PREPARACION`, `LISTO` o `ENTREGADO`.
- La hora se convierte a local usando `timezone_offset_minutes` antes de agrupar.
- Útil para planear staffing y promociones por categoría y horario.


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
  "fecha_hora": "datetime (ISO 8601, UTC)",
  "total": "float",
  "estado": "EstadoCompra",
  "detalles": "DetalleCompra[]",
  "qr": "QR | null",
  
  // Timestamps de cada etapa (UTC)
  "fecha_en_preparacion": "datetime | null",
  "fecha_listo": "datetime | null",
  "fecha_entregado": "datetime | null",
  
  // Tiempos calculados automáticamente (en segundos)
  "tiempo_hasta_preparacion": "float | null",  // Tiempo desde creación hasta inicio de preparación
  "tiempo_preparacion": "float | null",        // Tiempo de preparación (desde inicio hasta listo)
  "tiempo_espera_entrega": "float | null",     // Tiempo de espera para recoger (desde listo hasta entregado)
  "tiempo_total": "float | null"               // Tiempo total del proceso (desde creación hasta entrega)
}
```

**Nota sobre tiempos:** Los tiempos calculados se devuelven en **segundos**. Divide entre 60 para obtener minutos. Los timestamps se guardan en **UTC**.

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

## 📊 Medición de Tiempos en Compras

El sistema registra automáticamente **timestamps en UTC** cada vez que una compra cambia de estado, permitiendo medir con precisión los tiempos de cada etapa del proceso.

### Timestamps Registrados

| Campo | Cuándo se registra | Descripción |
|-------|-------------------|-------------|
| `fecha_hora` | Al crear la compra | Momento en que el usuario realiza y paga el pedido |
| `fecha_en_preparacion` | Al cambiar a `EN_PREPARACION` | Momento en que el staff comienza a preparar la orden |
| `fecha_listo` | Al cambiar a `LISTO` | Momento en que la orden está lista para recoger |
| `fecha_entregado` | Al cambiar a `ENTREGADO` o escanear QR | Momento en que se entrega la orden al cliente |

### Tiempos Calculados Automáticamente

Estos campos se calculan automáticamente en la respuesta (no se guardan en la BD):

| Campo | Fórmula | Qué mide |
|-------|---------|----------|
| `tiempo_hasta_preparacion` | `fecha_en_preparacion - fecha_hora` | Tiempo de espera antes de que comience la preparación |
| `tiempo_preparacion` | `fecha_listo - fecha_en_preparacion` | Duración de la preparación de la orden |
| `tiempo_espera_entrega` | `fecha_entregado - fecha_listo` | Tiempo que el cliente tardó en recoger su orden |
| `tiempo_total` | `fecha_entregado - fecha_hora` | Duración total del proceso (de principio a fin) |

### Ejemplo Visual del Flujo

```
PAGADO ──────► EN_PREPARACION ──────► LISTO ──────► ENTREGADO
│              │                      │             │
18:45:00       18:47:30               18:55:15      19:02:45
│              │                      │             │
└──150 seg────►└────465 seg─────────►└──450 seg──►│
(2.5 min)      (7.75 min)             (7.5 min)    
                                                    
◄────────────────── 1065 seg total ─────────────────►
                    (17.75 min)
```

### Uso de los Tiempos

**Para convertir a minutos:**
```javascript
const minutos = tiempo_en_segundos / 60;
// Ejemplo: 1065 / 60 = 17.75 minutos
```

**Para análisis y métricas:**
- **Eficiencia de cocina:** Analizar `tiempo_preparacion` promedio
- **Tiempo de respuesta:** Monitorear `tiempo_hasta_preparacion`
- **Comportamiento de clientes:** Estudiar `tiempo_espera_entrega`
- **Performance general:** Seguimiento de `tiempo_total`

**Nota:** Todos los timestamps usan **UTC** para evitar problemas de zona horaria. Convierte a hora local según sea necesario.

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

