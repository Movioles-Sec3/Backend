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
                imagen_url="https://api.lalicorera.com/storage/productos/licores/84257633-corona-extra.webp"
            ),
            Producto(
                nombre="Club Colombia",
                descripcion="Cerveza colombiana premium",
                precio=7000.0,
                id_tipo=1,
                imagen_url="https://kyva.co/wp-content/uploads/2025/07/Club-Colombia-Dorada_330ML_-800x1000PX_Transparente.png"
            ),
            Producto(
                nombre="Stella Artois",
                descripcion="Cerveza belga clásica",
                precio=9000.0,
                id_tipo=1,
                imagen_url="https://www.stellaartois.com.mx/sites/g/files/seuoyk556/files/2022-08/stella-artois%201.png.webp"
            ),

            # Cócteles
            Producto(
                nombre="Mojito",
                descripcion="Ron blanco, menta, limón y soda",
                precio=15000.0,
                id_tipo=2,
                imagen_url="https://api.lalicorera.com/storage/cocteles/recetas/86099316-mojito1.webp"
            ),
            Producto(
                nombre="Piña Colada",
                descripcion="Ron, piña y coco",
                precio=18000.0,
                id_tipo=2,
                imagen_url="https://api.lalicorera.com/storage/cocteles/recetas/86104877-pina-colada1.webp"
            ),
            Producto(
                nombre="Margarita",
                descripcion="Tequila, triple sec y limón",
                precio=16000.0,
                id_tipo=2,
                imagen_url="https://thecookinglab.es/wp-content/uploads/2024/08/Coctel-margarita-receta-500x500.jpg"
            ),

            # Tapas
            Producto(
                nombre="Nachos",
                descripcion="Tortillas con queso y guacamole",
                precio=12000.0,
                id_tipo=3,
                imagen_url="https://assets.tmecosys.com/image/upload/t_web_rdp_recipe_584x480/img/recipe/ras/Assets/7695121e-8b9a-4d00-ab96-4430e47266ba/Derivates/445ffdd9-9a8e-48fa-9e86-84c1e94469ca.jpg"
            ),
            Producto(
                nombre="Alitas BBQ",
                descripcion="Alitas de pollo en salsa barbacoa",
                precio=14000.0,
                id_tipo=3,
                imagen_url="https://www.unileverfoodsolutions.com.co/dam/global-ufs/mcos/NOLA/calcmenu/recipes/col-recipies/fruco/ALITAS-SALSA-1024X1024-px.jpg"
            ),
            Producto(
                nombre="Quesadillas",
                descripcion="Tortillas con queso y pollo",
                precio=10000.0,
                id_tipo=3,
                imagen_url="https://recetasdecocina.elmundo.es/wp-content/uploads/2025/01/quesadillas-1024x683.jpg"
            ),

            # Bebidas sin alcohol
            Producto(
                nombre="Coca Cola",
                descripcion="Gaseosa clásica",
                precio=4000.0,
                id_tipo=4,
                imagen_url="https://www.coca-cola.com/content/dam/onexp/co/es/brands/coca-cola/coca-cola-original/ccso_600ml_750x750.png"
            ),
            Producto(
                nombre="Agua con gas", 
                descripcion="Agua mineral con gas", 
                precio=3000.0,
                id_tipo=4,
                imagen_url="https://olimpica.vtexassets.com/arquivos/ids/1432000/7702090023008.jpg?v=638827638188730000"
            ),
            Producto(
                nombre="Jugo de naranja", 
                descripcion="Jugo natural de naranja", 
                precio=5000.0,
                id_tipo=4,
                imagen_url="https://olimpica.vtexassets.com/arquivos/ids/735793/7701008099869.jpg?v=637782322992670000"
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
