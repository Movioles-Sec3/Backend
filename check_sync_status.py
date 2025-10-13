"""
Script para verificar el estado de la replicación entre local y nube
Ejecutar con: python check_sync_status.py
"""

from sqlalchemy.orm import Session
from database import SessionLocal, setup_cloud_replication
from models import Usuario, TipoProducto, Producto, Compra, DetalleCompra, QR, EncuestaSeatDelivery
import config

def check_sync_status():
    """Verificar el estado de sincronización entre local y nube"""
    
    print("=" * 70)
    print("  VERIFICACIÓN DE ESTADO DE SINCRONIZACIÓN")
    print("=" * 70)
    
    print(f"\n📊 Configuración actual:")
    print(f"   Modo de BD: {config.DATABASE_MODE}")
    print(f"   BD Local: {config.LOCAL_DATABASE_URL}")
    print(f"   BD Nube: {config.CLOUD_DATABASE_URL if config.CLOUD_DATABASE_URL else 'No configurada'}")
    print(f"   Auto-sync: {'✅ Habilitado' if config.AUTO_SYNC_TO_CLOUD else '❌ Deshabilitado'}")
    
    if not config.CLOUD_DATABASE_URL:
        print("\n⚠️  Base de datos en la nube no configurada")
        print("   Configure CLOUD_DATABASE_URL en .env para habilitar sincronización")
        return
    
    # Configurar replicación
    setup_cloud_replication()
    
    # Importar después de configurar
    from database import CloudSessionLocal
    
    if not CloudSessionLocal:
        print("\n❌ No se pudo conectar a la base de datos en la nube")
        return
    
    local_db = SessionLocal()
    cloud_db = CloudSessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("  COMPARACIÓN DE REGISTROS")
        print("=" * 70)
        
        models_to_check = [
            ("Tipos de Producto", TipoProducto),
            ("Productos", Producto),
            ("Usuarios", Usuario),
            ("Compras", Compra),
            ("Detalles de Compra", DetalleCompra),
            ("Códigos QR", QR),
            ("Encuestas Seat Delivery", EncuestaSeatDelivery),
        ]
        
        total_local = 0
        total_cloud = 0
        all_synced = True
        
        print(f"\n{'Tabla':<25} {'Local':<10} {'Nube':<10} {'Estado'}")
        print("-" * 70)
        
        for model_name, model_class in models_to_check:
            local_count = local_db.query(model_class).count()
            cloud_count = cloud_db.query(model_class).count()
            
            total_local += local_count
            total_cloud += cloud_count
            
            if local_count == cloud_count:
                status = "✅ Sincronizado"
            else:
                status = f"⚠️  Diferencia: {abs(local_count - cloud_count)}"
                all_synced = False
            
            print(f"{model_name:<25} {local_count:<10} {cloud_count:<10} {status}")
        
        print("-" * 70)
        print(f"{'TOTAL':<25} {total_local:<10} {total_cloud:<10}")
        
        print("\n" + "=" * 70)
        print("  RESUMEN")
        print("=" * 70)
        
        if all_synced:
            print("\n✅ ¡Excelente! Todas las tablas están sincronizadas")
        else:
            print("\n⚠️  Hay diferencias entre local y nube")
            print("   Ejecuta 'python sync_to_cloud.py' para sincronizar")
        
        # Verificar conexión
        print("\n📡 Test de conectividad:")
        try:
            from sqlalchemy import text
            local_db.execute(text("SELECT 1"))
            print("   ✅ Conexión local: OK")
        except Exception as e:
            print(f"   ❌ Conexión local: ERROR - {e}")
        
        try:
            from sqlalchemy import text
            cloud_db.execute(text("SELECT 1"))
            print("   ✅ Conexión nube: OK")
        except Exception as e:
            print(f"   ❌ Conexión nube: ERROR - {e}")
        
        # Últimos registros
        print("\n📋 Últimas 5 compras en cada base de datos:")
        
        print("\n   Local:")
        local_compras = local_db.query(Compra).order_by(Compra.id.desc()).limit(5).all()
        if local_compras:
            for compra in local_compras:
                print(f"   - Compra #{compra.id}: {compra.estado.value} (${compra.total:,.0f})")
        else:
            print("   - No hay compras")
        
        print("\n   Nube:")
        cloud_compras = cloud_db.query(Compra).order_by(Compra.id.desc()).limit(5).all()
        if cloud_compras:
            for compra in cloud_compras:
                print(f"   - Compra #{compra.id}: {compra.estado.value} (${compra.total:,.0f})")
        else:
            print("   - No hay compras")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
    finally:
        local_db.close()
        cloud_db.close()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_sync_status()
