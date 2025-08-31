from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Producto, TipoProducto
from schemas import (
    ProductoResponse, 
    ProductoCreate, 
    ProductoUpdate, 
    TipoProductoResponse,
    TipoProductoCreate
)

router = APIRouter(prefix="/productos", tags=["productos"])

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    id_tipo: Optional[int] = None,
    disponible: bool = True,
    db: Session = Depends(get_db)
):
    """Listar todos los productos disponibles (el menú). Permitir filtrar por id_tipo"""
    query = db.query(Producto).filter(Producto.disponible == disponible)
    
    if id_tipo:
        query = query.filter(Producto.id_tipo == id_tipo)
    
    productos = query.all()
    return productos

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener detalles de un producto específico"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return producto

@router.get("/tipos/", response_model=List[TipoProductoResponse])
def listar_tipos_producto(db: Session = Depends(get_db)):
    """Listar todos los tipos de producto (categorías del menú)"""
    tipos = db.query(TipoProducto).all()
    return tipos

# Endpoints de administración (requieren autenticación de admin)
@router.post("/tipos/", response_model=TipoProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_tipo_producto(tipo: TipoProductoCreate, db: Session = Depends(get_db)):
    """(Admin) Crear un nuevo tipo de producto"""
    # Verificar si el tipo ya existe
    db_tipo = db.query(TipoProducto).filter(TipoProducto.nombre == tipo.nombre).first()
    if db_tipo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de producto ya existe"
        )
    
    db_tipo = TipoProducto(nombre=tipo.nombre)
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    
    return db_tipo

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """(Admin) Crear un nuevo producto"""
    # Verificar que el tipo de producto existe
    tipo_producto = db.query(TipoProducto).filter(TipoProducto.id == producto.id_tipo).first()
    if not tipo_producto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de producto no existe"
        )
    
    db_producto = Producto(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        imagen_url=producto.imagen_url,
        precio=producto.precio,
        disponible=producto.disponible,
        id_tipo=producto.id_tipo
    )
    
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    return db_producto

@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int, 
    producto_update: ProductoUpdate, 
    db: Session = Depends(get_db)
):
    """(Admin) Actualizar un producto"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Verificar que el tipo de producto existe
    tipo_producto = db.query(TipoProducto).filter(TipoProducto.id == producto_update.id_tipo).first()
    if not tipo_producto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de producto no existe"
        )
    
    # Actualizar campos
    producto.nombre = producto_update.nombre
    producto.descripcion = producto_update.descripcion
    producto.imagen_url = producto_update.imagen_url
    producto.precio = producto_update.precio
    producto.disponible = producto_update.disponible
    producto.id_tipo = producto_update.id_tipo
    
    db.commit()
    db.refresh(producto)
    
    return producto
