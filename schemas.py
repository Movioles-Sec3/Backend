from pydantic import BaseModel, EmailStr, computed_field
from typing import List, Optional
from datetime import datetime
from models import EstadoCompra, EstadoQR, NivelInteresSeatDelivery

# Esquemas de Usuario
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: int
    saldo: float
    encuesta: Optional['EncuestaSeatDeliveryResponse'] = None
    
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

# Encuesta Seat Delivery
class EncuestaSeatDeliveryBase(BaseModel):
    nivel_interes: NivelInteresSeatDelivery
    minutos_extra: int
    comentarios: Optional[str] = None

class EncuestaSeatDeliveryCreate(EncuestaSeatDeliveryBase):
    pass

class EncuestaSeatDeliveryResponse(EncuestaSeatDeliveryBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True

UsuarioResponse.model_rebuild()

# --- Esquemas de Analytics ---
class CategoryReorderHourCount(BaseModel):
    hour: int
    count: int

class CategoryReorderStats(BaseModel):
    categoria_id: int
    categoria_nombre: str
    reorder_count: int
    hour_distribution: List[CategoryReorderHourCount]
    peak_hours: List[int]

class ReordersByCategoryResponse(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    timezone_offset_minutes: int
    categories: List[CategoryReorderStats]

# Order Peak Hours Schemas
class HourlyDistribution(BaseModel):
    hour: int
    order_count: int
    total_revenue: float
    avg_order_value: float
    percentage: float
    is_peak: bool

class OrderPeakHoursSummary(BaseModel):
    total_orders: int
    peak_hours: List[int]
    peak_hour_range: str
    orders_in_peak_hours: int
    percentage_in_peak_hours: float
    busiest_hour: int
    busiest_hour_orders: int
    slowest_hour: int
    slowest_hour_orders: int

class OrderPeakHoursResponse(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    timezone_offset_minutes: int
    hourly_distribution: List[HourlyDistribution]
    peak_hours: List[int]
    summary: OrderPeakHoursSummary


# --- Esquemas para Recargas ---
class RecargaEventoResponse(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: str
    usuario_email: EmailStr
    monto: float
    fecha_hora: datetime
