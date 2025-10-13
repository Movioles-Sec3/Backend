"""
Script para probar la sincronización automática
"""
import requests
import time

BASE_URL = "http://localhost:8080"

print("=" * 70)
print("  PRUEBA DE SINCRONIZACIÓN AUTOMÁTICA")
print("=" * 70)

# 1. Ver estado inicial
print("\n1️⃣ Estado inicial de sincronización:")
response = requests.get(f"{BASE_URL}/admin/sync-status")
if response.status_code == 200:
    data = response.json()
    print(f"   Usuarios en local: {data['local_stats']['usuarios']}")
    print(f"   Usuarios en nube: {data['cloud_stats']['usuarios']}")
    print(f"   Estado: {data['sync_status']}")
else:
    print(f"   ❌ Error: {response.status_code}")
    exit(1)

# 2. Crear un nuevo usuario
print("\n2️⃣ Creando un nuevo usuario...")
nuevo_usuario = {
    "nombre": "Test Automatico",
    "email": f"test.auto.{int(time.time())}@test.com",
    "password": "123456"
}

response = requests.post(f"{BASE_URL}/usuarios/", json=nuevo_usuario)
if response.status_code == 201:
    usuario = response.json()
    print(f"   ✅ Usuario creado: {usuario['nombre']} ({usuario['email']})")
    print(f"   ID: {usuario['id']}")
else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   {response.text}")
    exit(1)

# 3. Esperar un momento para que se sincronice
print("\n3️⃣ Esperando sincronización automática...")
time.sleep(2)

# 4. Verificar sincronización
print("\n4️⃣ Verificando sincronización:")
response = requests.get(f"{BASE_URL}/admin/sync-status")
if response.status_code == 200:
    data = response.json()
    print(f"   Usuarios en local: {data['local_stats']['usuarios']}")
    print(f"   Usuarios en nube: {data['cloud_stats']['usuarios']}")
    print(f"   Estado: {data['sync_status']}")
    
    if data['sync_status'] == 'synced':
        print("\n✅ ¡Sincronización automática funcionando perfectamente!")
    else:
        print("\n⚠️  Hay diferencias. Puede que la sincronización esté en proceso.")
else:
    print(f"   ❌ Error: {response.status_code}")

print("\n" + "=" * 70)
