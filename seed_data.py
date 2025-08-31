"""
Script para poblar la base de datos con datos de prueba
Ejecutar con: python seed_data.py
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Usuario, TipoProducto, Producto
from auth import get_password_hash

def create_tables():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)

def seed_data():
    """Poblar la base de datos con datos de prueba"""
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Usuario).first():
            print("La base de datos ya tiene datos. Saltando seed...")
            return
        
        print("Poblando base de datos con datos de prueba...")
        
        # Crear usuario de prueba
        usuario_test = Usuario(
            nombre="Juan Pérez",
            email="juan@test.com",
            password=get_password_hash("123456"),
            saldo=50000.0  # $50,000 de saldo inicial
        )
        db.add(usuario_test)
        
        # Crear tipos de producto
        tipos = [
            TipoProducto(nombre="Cervezas"),
            TipoProducto(nombre="Cócteles"),
            TipoProducto(nombre="Tapas"),
            TipoProducto(nombre="Bebidas sin alcohol")
        ]
        
        for tipo in tipos:
            db.add(tipo)
        
        db.commit()  # Commit para obtener los IDs
        
        # Crear productos de ejemplo
        productos = [
            # Cervezas
            Producto(
                nombre="Corona", 
                descripcion="Cerveza mexicana ligera", 
                precio=8000.0,
                id_tipo=1,
                imagen_url="https://example.com/corona.jpg"
            ),
            Producto(
                nombre="Club Colombia", 
                descripcion="Cerveza colombiana premium", 
                precio=7000.0,
                id_tipo=1,
                imagen_url="https://example.com/club.jpg"
            ),
            Producto(
                nombre="Stella Artois", 
                descripcion="Cerveza belga clásica", 
                precio=9000.0,
                id_tipo=1,
                imagen_url="https://example.com/stella.jpg"
            ),
            
            # Cócteles
            Producto(
                nombre="Mojito", 
                descripcion="Ron blanco, menta, limón y soda", 
                precio=15000.0,
                id_tipo=2,
                imagen_url="https://example.com/mojito.jpg"
            ),
            Producto(
                nombre="Piña Colada", 
                descripcion="Ron, piña y coco", 
                precio=18000.0,
                id_tipo=2,
                imagen_url="https://example.com/pina.jpg"
            ),
            Producto(
                nombre="Margarita", 
                descripcion="Tequila, triple sec y limón", 
                precio=16000.0,
                id_tipo=2,
                imagen_url="https://example.com/margarita.jpg"
            ),
            
            # Tapas
            Producto(
                nombre="Nachos", 
                descripcion="Tortillas con queso y guacamole", 
                precio=12000.0,
                id_tipo=3,
                imagen_url="https://example.com/nachos.jpg"
            ),
            Producto(
                nombre="Alitas BBQ", 
                descripcion="Alitas de pollo en salsa barbacoa", 
                precio=14000.0,
                id_tipo=3,
                imagen_url="https://example.com/alitas.jpg"
            ),
            Producto(
                nombre="Quesadillas", 
                descripcion="Tortillas con queso y pollo", 
                precio=10000.0,
                id_tipo=3,
                imagen_url="https://example.com/quesadillas.jpg"
            ),
            
            # Bebidas sin alcohol
            Producto(
                nombre="Coca Cola", 
                descripcion="Gaseosa clásica", 
                precio=4000.0,
                id_tipo=4,
                imagen_url="https://example.com/coca.jpg"
            ),
            Producto(
                nombre="Agua con gas", 
                descripcion="Agua mineral con gas", 
                precio=3000.0,
                id_tipo=4,
                imagen_url="https://example.com/agua.jpg"
            ),
            Producto(
                nombre="Jugo de naranja", 
                descripcion="Jugo natural de naranja", 
                precio=5000.0,
                id_tipo=4,
                imagen_url="https://example.com/jugo.jpg"
            ),
        ]
        
        for producto in productos:
            db.add(producto)
        
        db.commit()
        print("✅ Base de datos poblada exitosamente!")
        print("Usuario de prueba: juan@test.com / 123456")
        print("Saldo inicial: $50,000")
        
    except Exception as e:
        print(f"❌ Error al poblar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()
