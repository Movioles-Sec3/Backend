"""
Script para probar la sincronización offline
Simula la creación de usuarios sin conexión a internet
"""

import os
os.environ['AUTO_SYNC_TO_CLOUD'] = 'true'
os.environ['CLOUD_DATABASE_URL'] = 'postgresql://invalid:invalid@localhost:5432/invalid'

from database import SessionLocal, setup_cloud_replication, register_sync_events
from models import Usuario
from auth import get_password_hash
import time

print("="*60)
print("TEST DE SINCRONIZACIÓN OFFLINE")
print("="*60)
print()

# Configurar (con URL inválida para simular sin internet)
setup_cloud_replication()
register_sync_events()

print("\n1️⃣ Creando usuario SIN CONEXIÓN a internet...")
print("-"*60)

db = SessionLocal()

# Crear usuario
nuevo_usuario = Usuario(
    nombre="Test Offline",
    email="offline@test.com",
    password=get_password_hash("123456"),
    saldo=0.0
)

db.add(nuevo_usuario)
db.commit()
db.refresh(nuevo_usuario)

print(f"✅ Usuario creado localmente: {nuevo_usuario.nombre} ({nuevo_usuario.email})")
print(f"   ID: {nuevo_usuario.id}")

db.close()

print("\n2️⃣ Esperando que el sistema intente sincronizar...")
print("-"*60)
print("   El sistema detectará que no hay internet")
print("   La operación quedará en cola esperando conexión")

time.sleep(5)

from database import get_sync_status

status = get_sync_status()

print(f"\n📊 ESTADO DE SINCRONIZACIÓN:")
print(f"   Internet disponible: {status['internet_available']}")
print(f"   Operaciones en cola: {status['queue_size']}")
print(f"   Thread activo: {status['sync_thread_alive']}")

if status['queue_size'] > 0:
    print(f"\n✅ TEST EXITOSO:")
    print(f"   - Usuario creado localmente")
    print(f"   - {status['queue_size']} operación(es) esperando en cola")
    print(f"   - Se sincronizará automáticamente cuando haya internet")
else:
    print(f"\n⚠️  La cola está vacía (esto no debería pasar)")

print("\n" + "="*60)