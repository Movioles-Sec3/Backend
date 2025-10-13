"""
Script para sincronizar manualmente toda la base de datos local a la nube
Útil para la primera sincronización o para recuperar datos
Ejecutar con: python sync_to_cloud.py
"""

from sqlalchemy.orm import Session
from database import SessionLocal, setup_cloud_replication
from models import Base, Usuario, TipoProducto, Producto, Compra, DetalleCompra, QR, EncuestaSeatDelivery
import config

def sync_all_data():
    """Sincronizar todos los datos de la base de datos local a la nube"""
    
    # Configurar replicación
    setup_cloud_replication()
    
    # Importar después de configurar
    from database import CloudSessionLocal, cloud_engine
    
    if not CloudSessionLocal:
        print("❌ No se pudo establecer conexión con la base de datos en la nube")
        print("   Verifica que CLOUD_DATABASE_URL esté configurada correctamente en .env")
        return
    
    print("🔄 Iniciando sincronización completa a la nube...")
    
    local_db = SessionLocal()
    cloud_db = CloudSessionLocal()
    
    try:
        # Crear las tablas en la nube si no existen
        print("📊 Creando tablas en la nube...")
        Base.metadata.create_all(bind=cloud_engine)
        
        # Lista de modelos a sincronizar (en orden de dependencias)
        models_to_sync = [
            ("Tipos de Producto", TipoProducto),
            ("Productos", Producto),
            ("Usuarios", Usuario),
            ("Compras", Compra),
            ("Detalles de Compra", DetalleCompra),
            ("Códigos QR", QR),
            ("Encuestas Seat Delivery", EncuestaSeatDelivery),
        ]
        
        total_synced = 0
        
        for model_name, model_class in models_to_sync:
            print(f"\n🔄 Sincronizando {model_name}...")
            
            # Obtener todos los registros de la base de datos local
            local_records = local_db.query(model_class).all()
            
            if not local_records:
                print(f"   ℹ️  No hay registros de {model_name} para sincronizar")
                continue
            
            synced_count = 0
            
            for record in local_records:
                try:
                    # Usar merge para insertar o actualizar
                    cloud_db.merge(record)
                    synced_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error al sincronizar registro: {e}")
            
            cloud_db.commit()
            total_synced += synced_count
            print(f"   ✅ {synced_count} registros de {model_name} sincronizados")
        
        print(f"\n✅ Sincronización completa exitosa!")
        print(f"📊 Total de registros sincronizados: {total_synced}")
        
        # Verificar conteos
        print("\n📊 Verificando sincronización...")
        for model_name, model_class in models_to_sync:
            local_count = local_db.query(model_class).count()
            cloud_count = cloud_db.query(model_class).count()
            status = "✅" if local_count == cloud_count else "⚠️"
            print(f"{status} {model_name}: Local={local_count}, Nube={cloud_count}")
        
    except Exception as e:
        print(f"\n❌ Error durante la sincronización: {e}")
        cloud_db.rollback()
    finally:
        local_db.close()
        cloud_db.close()

def clear_cloud_database():
    """CUIDADO: Elimina todos los datos de la base de datos en la nube"""
    setup_cloud_replication()
    
    # Importar después de configurar
    from database import CloudSessionLocal, cloud_engine
    
    if not CloudSessionLocal:
        print("❌ No se pudo establecer conexión con la base de datos en la nube")
        return
    
    response = input("⚠️  ¿Estás seguro de que deseas eliminar TODOS los datos de la nube? (escribe 'SI' para confirmar): ")
    
    if response != "SI":
        print("❌ Operación cancelada")
        return
    
    print("🗑️  Eliminando todos los datos de la nube...")
    
    try:
        # Eliminar todas las tablas
        Base.metadata.drop_all(bind=cloud_engine)
        print("✅ Base de datos en la nube limpiada exitosamente")
        
        # Recrear las tablas vacías
        Base.metadata.create_all(bind=cloud_engine)
        print("✅ Tablas recreadas")
        
    except Exception as e:
        print(f"❌ Error al limpiar la base de datos: {e}")

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("  SINCRONIZACIÓN DE BASE DE DATOS A LA NUBE")
    print("=" * 60)
    print(f"\nModo de base de datos: {config.DATABASE_MODE}")
    print(f"URL local: {config.LOCAL_DATABASE_URL}")
    print(f"URL nube: {config.CLOUD_DATABASE_URL if config.CLOUD_DATABASE_URL else 'No configurada'}")
    print("\nOpciones:")
    print("  1. Sincronizar todos los datos a la nube")
    print("  2. Limpiar base de datos en la nube (CUIDADO)")
    print("  3. Salir")
    
    choice = input("\nSelecciona una opción (1-3): ")
    
    if choice == "1":
        sync_all_data()
    elif choice == "2":
        clear_cloud_database()
    elif choice == "3":
        print("👋 Saliendo...")
    else:
        print("❌ Opción inválida")
