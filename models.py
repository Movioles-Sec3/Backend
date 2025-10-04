from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class EstadoCompra(enum.Enum):
    CARRITO = "CARRITO"
    PAGADO = "PAGADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    ENTREGADO = "ENTREGADO"

class EstadoQR(enum.Enum):
    ACTIVO = "ACTIVO"
    CANJEADO = "CANJEADO"
    EXPIRADO = "EXPIRADO"

class NivelInteresSeatDelivery(enum.Enum):
    ALTO = "HIGH"
    MODERADO = "MODERATE"
    BAJO = "LOW"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    saldo = Column(Float, default=0.0, nullable=False)
    
    # Relaciones
    compras = relationship("Compra", back_populates="usuario")
    encuesta = relationship("EncuestaSeatDelivery", back_populates="usuario", uselist=False)

class TipoProducto(Base):
    __tablename__ = "tipos_producto"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    
    # Relaciones
    productos = relationship("Producto", back_populates="tipo_producto")

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    imagen_url = Column(String)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True, nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipos_producto.id"), nullable=False)
    
    # Relaciones
    tipo_producto = relationship("TipoProducto", back_populates="productos")
    detalles_compra = relationship("DetalleCompra", back_populates="producto")

class Compra(Base):
    __tablename__ = "compras"
    
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_hora = Column(DateTime, default=func.now(), nullable=False)
    total = Column(Float, nullable=False)
    estado = Column(Enum(EstadoCompra), default=EstadoCompra.CARRITO, nullable=False)
    
    # Timestamps para medir tiempos entre estados
    fecha_en_preparacion = Column(DateTime, nullable=True)
    fecha_listo = Column(DateTime, nullable=True)
    fecha_entregado = Column(DateTime, nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="compras")
    detalles = relationship("DetalleCompra", back_populates="compra")
    qr = relationship("QR", back_populates="compra", uselist=False)

class DetalleCompra(Base):
    __tablename__ = "detalles_compra"
    
    id_compra = Column(Integer, ForeignKey("compras.id"), primary_key=True)
    id_producto = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False)
    precio_unitario_compra = Column(Float, nullable=False)
    
    # Relaciones
    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_compra")

class QR(Base):
    __tablename__ = "qrs"
    
    id_compra = Column(Integer, ForeignKey("compras.id"), primary_key=True)
    codigo_qr_hash = Column(String, unique=True, nullable=False)
    estado = Column(Enum(EstadoQR), default=EstadoQR.ACTIVO, nullable=False)
    
    # Relaciones
    compra = relationship("Compra", back_populates="qr")

class EncuestaSeatDelivery(Base):
    __tablename__ = "encuestas_seat_delivery"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)
    nivel_interes = Column(Enum(NivelInteresSeatDelivery), nullable=False)
    minutos_extra = Column(Integer, nullable=False)
    comentarios = Column(String)
    creado_en = Column(DateTime, default=func.now(), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="encuesta")
