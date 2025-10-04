from pydantic import BaseModel, EmailStr, computed_field
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
    
    # Timestamps de cada etapa
    fecha_en_preparacion: Optional[datetime] = None
    fecha_listo: Optional[datetime] = None
    fecha_entregado: Optional[datetime] = None
    
    # Tiempos calculados (en segundos)
    @computed_field
    @property
    def tiempo_hasta_preparacion(self) -> Optional[float]:
        """Tiempo desde creación hasta que comienza la preparación (segundos)"""
        if self.fecha_en_preparacion:
            return (self.fecha_en_preparacion - self.fecha_hora).total_seconds()
        return None
    
    @computed_field
    @property
    def tiempo_preparacion(self) -> Optional[float]:
        """Tiempo desde que comienza la preparación hasta que está lista (segundos)"""
        if self.fecha_en_preparacion and self.fecha_listo:
            return (self.fecha_listo - self.fecha_en_preparacion).total_seconds()
        return None
    
    @computed_field
    @property
    def tiempo_espera_entrega(self) -> Optional[float]:
        """Tiempo desde que está lista hasta que se entrega (segundos)"""
        if self.fecha_listo and self.fecha_entregado:
            return (self.fecha_entregado - self.fecha_listo).total_seconds()
        return None
    
    @computed_field
    @property
    def tiempo_total(self) -> Optional[float]:
        """Tiempo total desde creación hasta entrega (segundos)"""
        if self.fecha_entregado:
            return (self.fecha_entregado - self.fecha_hora).total_seconds()
        return None
    
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
