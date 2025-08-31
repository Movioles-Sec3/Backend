from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import EstadoCompra, EstadoQR

# Esquemas de Usuario
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: int
    saldo: float
    
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class RecargaSaldo(BaseModel):
    monto: float

# Esquemas de TipoProducto
class TipoProductoBase(BaseModel):
    nombre: str

class TipoProductoCreate(TipoProductoBase):
    pass

class TipoProductoResponse(TipoProductoBase):
    id: int
    
    class Config:
        from_attributes = True

# Esquemas de Producto
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    precio: float
    disponible: bool = True

class ProductoCreate(ProductoBase):
    id_tipo: int

class ProductoUpdate(ProductoBase):
    id_tipo: int

class ProductoResponse(ProductoBase):
    id: int
    id_tipo: int
    tipo_producto: TipoProductoResponse
    
    class Config:
        from_attributes = True

# Esquemas de DetalleCompra
class DetalleCompraBase(BaseModel):
    id_producto: int
    cantidad: int

class DetalleCompraCreate(DetalleCompraBase):
    pass

class DetalleCompraResponse(DetalleCompraBase):
    precio_unitario_compra: float
    producto: ProductoResponse
    
    class Config:
        from_attributes = True

# Esquemas de Compra
class CompraCreate(BaseModel):
    productos: List[DetalleCompraCreate]

class CompraResponse(BaseModel):
    id: int
    fecha_hora: datetime
    total: float
    estado: EstadoCompra
    detalles: List[DetalleCompraResponse]
    qr: Optional['QRResponse'] = None
    
    class Config:
        from_attributes = True

class CompraEstadoUpdate(BaseModel):
    estado: EstadoCompra

# Esquemas de QR
class QRResponse(BaseModel):
    codigo_qr_hash: str
    estado: EstadoQR
    
    class Config:
        from_attributes = True

class QREscanear(BaseModel):
    codigo_qr_hash: str

# Esquema para el token JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Para resolver la referencia circular
CompraResponse.model_rebuild()
