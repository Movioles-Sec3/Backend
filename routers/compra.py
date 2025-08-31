import hashlib
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Usuario, Compra, DetalleCompra, Producto, QR, EstadoCompra, EstadoQR
from schemas import (
    CompraCreate, 
    CompraResponse, 
    CompraEstadoUpdate,
    QREscanear,
    QRResponse
)
from auth import get_current_user

router = APIRouter(prefix="/compras", tags=["compras"])

def generar_codigo_qr() -> str:
    """Generar un código QR único"""
    unique_id = str(uuid.uuid4())
    return hashlib.sha256(unique_id.encode()).hexdigest()

@router.get("/me", response_model=List[CompraResponse])
def obtener_historial_compras(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el historial de compras del usuario autenticado"""
    compras = db.query(Compra).filter(
        Compra.id_usuario == current_user.id,
        Compra.estado != EstadoCompra.CARRITO
    ).all()
    return compras

@router.post("/", response_model=CompraResponse, status_code=status.HTTP_201_CREATED)
def crear_compra(
    compra_data: CompraCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint principal de negocio. Crear una nueva compra.
    Procesa el pago y genera el QR para la orden.
    """
    if not compra_data.productos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La compra debe tener al menos un producto"
        )
    
    # Calcular el total y verificar disponibilidad de productos
    total = 0.0
    productos_verificados = []
    
    for item in compra_data.productos:
        if item.cantidad <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad debe ser mayor a 0"
            )
        
        producto = db.query(Producto).filter(Producto.id == item.id_producto).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {item.id_producto} no encontrado"
            )
        
        if not producto.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto '{producto.nombre}' no está disponible"
            )
        
        subtotal = producto.precio * item.cantidad
        total += subtotal
        
        productos_verificados.append({
            "producto": producto,
            "cantidad": item.cantidad,
            "subtotal": subtotal
        })
    
    # Verificar que el usuario tenga saldo suficiente
    if current_user.saldo < total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Necesitas ${total:.2f}, tienes ${current_user.saldo:.2f}"
        )
    
    try:
        # Crear la compra
        nueva_compra = Compra(
            id_usuario=current_user.id,
            total=total,
            estado=EstadoCompra.PAGADO
        )
        db.add(nueva_compra)
        db.flush()  # Para obtener el ID de la compra
        
        # Crear los detalles de la compra
        for item in productos_verificados:
            detalle = DetalleCompra(
                id_compra=nueva_compra.id,
                id_producto=item["producto"].id,
                cantidad=item["cantidad"],
                precio_unitario_compra=item["producto"].precio
            )
            db.add(detalle)
        
        # Generar y guardar el QR
        codigo_qr = generar_codigo_qr()
        qr = QR(
            id_compra=nueva_compra.id,
            codigo_qr_hash=codigo_qr,
            estado=EstadoQR.ACTIVO
        )
        db.add(qr)
        
        # Descontar el saldo del usuario
        current_user.saldo -= total
        
        # Confirmar la transacción
        db.commit()
        db.refresh(nueva_compra)
        
        return nueva_compra
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la compra"
        )

@router.get("/pendientes", response_model=List[CompraResponse])
def listar_compras_pendientes(db: Session = Depends(get_db)):
    """(Staff) Listar todas las compras con estado 'PAGADO' o 'EN_PREPARACION'"""
    compras = db.query(Compra).filter(
        Compra.estado.in_([EstadoCompra.PAGADO, EstadoCompra.EN_PREPARACION])
    ).all()
    return compras

@router.put("/{compra_id}/estado", response_model=CompraResponse)
def actualizar_estado_compra(
    compra_id: int,
    estado_update: CompraEstadoUpdate,
    db: Session = Depends(get_db)
):
    """(Staff) Actualizar el estado de una compra"""
    compra = db.query(Compra).filter(Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra no encontrada"
        )
    
    # Validar transiciones de estado válidas
    estado_actual = compra.estado
    nuevo_estado = estado_update.estado
    
    transiciones_validas = {
        EstadoCompra.PAGADO: [EstadoCompra.EN_PREPARACION],
        EstadoCompra.EN_PREPARACION: [EstadoCompra.LISTO],
        EstadoCompra.LISTO: [EstadoCompra.ENTREGADO]
    }
    
    if estado_actual not in transiciones_validas or nuevo_estado not in transiciones_validas[estado_actual]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cambiar de estado {estado_actual.value} a {nuevo_estado.value}"
        )
    
    compra.estado = nuevo_estado
    db.commit()
    db.refresh(compra)
    
    return compra

@router.post("/qr/escanear", response_model=dict)
def escanear_qr(
    qr_data: QREscanear,
    db: Session = Depends(get_db)
):
    """(Staff) Recibir un codigo_qr_hash, verificarlo y procesar la entrega"""
    qr = db.query(QR).filter(QR.codigo_qr_hash == qr_data.codigo_qr_hash).first()
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código QR no válido"
        )
    
    if qr.estado != EstadoQR.ACTIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El código QR ya fue {qr.estado.value.lower()}"
        )
    
    compra = qr.compra
    if compra.estado != EstadoCompra.LISTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La orden no está lista para entregar. Estado actual: {compra.estado.value}"
        )
    
    # Marcar QR como canjeado y compra como entregada
    qr.estado = EstadoQR.CANJEADO
    compra.estado = EstadoCompra.ENTREGADO
    
    db.commit()
    
    return {
        "mensaje": "Orden entregada exitosamente",
        "compra_id": compra.id,
        "cliente": compra.usuario.nombre,
        "total": compra.total
    }
