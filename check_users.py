"""
Script para verificar usuarios - Version sin emojis para Windows
"""
import sys
import io

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import database
from models import Usuario

database.setup_cloud_replication()

print("=" * 60)
print("VERIFICACION DE SINCRONIZACION DE USUARIOS")
print("=" * 60)

# Contar en local
local_db = database.SessionLocal()
local_count = local_db.query(Usuario).count()
local_users = local_db.query(Usuario).all()
print(f"\nUSUARIOS EN LOCAL: {local_count}")
for user in local_users:
    print(f"   - {user.email} (ID: {user.id})")
local_db.close()

# Contar en nube
if database.CloudSessionLocal:
    cloud_db = database.CloudSessionLocal()
    cloud_count = cloud_db.query(Usuario).count()
    cloud_users = cloud_db.query(Usuario).all()
    print(f"\nUSUARIOS EN NUBE: {cloud_count}")
    for user in cloud_users:
        print(f"   - {user.email} (ID: {user.id})")
    cloud_db.close()
    
    # Comparar
    print(f"\n" + "=" * 60)
    if local_count == cloud_count:
        print("[OK] SINCRONIZACION CORRECTA - Misma cantidad de usuarios")
    else:
        diff = local_count - cloud_count
        print(f"[ERROR] PROBLEMA - Faltan {diff} usuarios en la nube")
        print(f"   Ejecuta: python sync_to_cloud.py")
    print("=" * 60)
else:
    print("\n[ADVERTENCIA] No hay conexion a la nube")
    print("   Verifica que CLOUD_DATABASE_URL este configurada en .env")
