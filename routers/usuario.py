from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario, EncuestaSeatDelivery, RecargaSaldoEvento
from schemas import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioLogin,
    Token,
    RecargaSaldo,
    EncuestaSeatDeliveryCreate,
    EncuestaSeatDeliveryResponse,
)
from auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario (registro)"""
    # Verificar si el email ya existe
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear el usuario con contraseña hasheada
    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password=hashed_password,
        saldo=0.0
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.post("/token", response_model=Token)
def login_usuario(usuario_login: UsuarioLogin, db: Session = Depends(get_db)):
    """Login de usuario para obtener un token JWT"""
    user = authenticate_user(db, usuario_login.email, usuario_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(current_user: Usuario = Depends(get_current_user)):
    """Obtener detalles del usuario autenticado"""
    return current_user

@router.post("/me/recargar", response_model=UsuarioResponse)
def recargar_saldo(
    recarga: RecargaSaldo,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Añadir saldo al monedero del usuario"""
    if recarga.monto <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto debe ser mayor a 0"
        )
    # Actualizar saldo y registrar evento de recarga en la misma transacción
    current_user.saldo += recarga.monto
    evento = RecargaSaldoEvento(id_usuario=current_user.id, monto=recarga.monto)
    db.add(evento)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/encuesta", response_model=EncuestaSeatDeliveryResponse, status_code=status.HTTP_201_CREATED)
def crear_encuesta_usuario(
    encuesta_data: EncuestaSeatDeliveryCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar la preferencia de seat delivery del usuario"""
    if current_user.encuesta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene una encuesta registrada. Usa PUT para actualizarla."
        )

    encuesta = EncuestaSeatDelivery(
        id_usuario=current_user.id,
        nivel_interes=encuesta_data.nivel_interes,
        minutos_extra=encuesta_data.minutos_extra,
        comentarios=encuesta_data.comentarios
    )

    db.add(encuesta)
    db.commit()
    db.refresh(encuesta)

    return encuesta


@router.put("/me/encuesta", response_model=EncuestaSeatDeliveryResponse)
def actualizar_encuesta_usuario(
    encuesta_data: EncuestaSeatDeliveryCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar la encuesta registrada del usuario"""
    encuesta = current_user.encuesta
    if not encuesta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene una encuesta registrada"
        )

    encuesta.nivel_interes = encuesta_data.nivel_interes
    encuesta.minutos_extra = encuesta_data.minutos_extra
    encuesta.comentarios = encuesta_data.comentarios

    db.commit()
    db.refresh(encuesta)

    return encuesta


@router.get("/me/encuesta", response_model=EncuestaSeatDeliveryResponse)
def obtener_encuesta_usuario(
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener la encuesta guardada del usuario autenticado"""
    encuesta = current_user.encuesta
    if not encuesta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene una encuesta registrada"
        )

    return encuesta
