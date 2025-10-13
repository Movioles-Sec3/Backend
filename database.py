from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import config
import threading
import time
import queue
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la base de datos principal
SQLALCHEMY_DATABASE_URL = config.get_database_url()

# Configurar connect_args según el tipo de base de datos
connect_args = {}
if config.is_sqlite():
    connect_args = {"check_same_thread": False}

# Engine principal
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Sistema de Replicación a la Nube con Cola de Reintentos ---

cloud_engine: Optional[any] = None
CloudSessionLocal: Optional[sessionmaker] = None

# Cola de operaciones pendientes
sync_queue = queue.Queue()
sync_thread = None
is_syncing = False
internet_available = True
last_connection_check = None
syncing_objects = set()  # Track objects being synced to avoid loops
sync_lock = threading.Lock()  # Lock for thread-safe operations

def check_internet_connection():
    """Verificar si hay conexión a internet probando la conexión a la nube"""
    global internet_available, last_connection_check
    
    # Cachear el resultado por 10 segundos
    now = time.time()
    if last_connection_check and (now - last_connection_check) < 10:
        return internet_available
    
    if not CloudSessionLocal:
        internet_available = False
        return False
    
    try:
        from sqlalchemy import text
        with cloud_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        internet_available = True
        last_connection_check = now
        logger.info("✅ Conexión a internet OK")
        return True
    except UnicodeDecodeError:
        # Error de decodificación - sin conexión
        internet_available = False
        last_connection_check = now
        logger.warning("❌ Sin conexión a la base de datos en la nube")
        return False
    except Exception as e:
        internet_available = False
        last_connection_check = now
        # Silenciar el error completo, solo mostrar mensaje simple
        logger.warning("❌ Sin conexión a la base de datos en la nube")
        return False

def save_to_sync_queue(operation_type, model_name, data, pk_filter):
    """Guardar operación en la cola de sincronización"""
    operation = {
        'type': operation_type,  # 'insert', 'update', 'delete'
        'model': model_name,
        'data': data,
        'pk_filter': pk_filter,
        'timestamp': datetime.utcnow().isoformat(),
        'retry_count': 0
    }
    sync_queue.put(operation)
    logger.info(f"📝 Operación {operation_type} en {model_name} agregada a la cola (tamaño: {sync_queue.qsize()})")

def process_sync_queue():
    """Procesar la cola de sincronización en background"""
    global is_syncing
    
    logger.info("🔄 Iniciando proceso de sincronización en background")
    
    while True:
        try:
            # Esperar hasta que haya operaciones en la cola
            if sync_queue.empty():
                time.sleep(1)
                continue
            
            # Verificar conexión a internet antes de procesar
            if not check_internet_connection():
                logger.warning("⏳ Esperando conexión a internet... (reintentando en 30s)")
                time.sleep(30)  # Esperar 30 segundos antes de reintentar
                continue
            
            # Procesar operación
            operation = sync_queue.get(block=False)
            
            try:
                success = execute_sync_operation(operation)
                
                if success:
                    logger.info(f"✅ Sincronizado: {operation['type']} en {operation['model']}")
                    sync_queue.task_done()
                else:
                    # Reintentar si falló
                    operation['retry_count'] += 1
                    if operation['retry_count'] < 5:  # Máximo 5 reintentos
                        logger.warning(f"⚠️  Reintento {operation['retry_count']}/5 para {operation['type']} en {operation['model']}")
                        time.sleep(2 ** operation['retry_count'])  # Backoff exponencial
                        sync_queue.put(operation)
                    else:
                        logger.error(f"❌ Operación descartada después de 5 reintentos: {operation}")
                    sync_queue.task_done()
                    
            except Exception as e:
                logger.error(f"❌ Error procesando operación: {e}")
                sync_queue.task_done()
                
        except queue.Empty:
            time.sleep(1)
        except Exception as e:
            logger.error(f"❌ Error en proceso de sincronización: {e}")
            time.sleep(5)

def execute_sync_operation(operation):
    """Ejecutar una operación de sincronización"""
    if not CloudSessionLocal:
        return False
    
    try:
        cloud_db = CloudSessionLocal()
        
        # Importar el modelo dinámicamente
        from models import Usuario, Producto, TipoProducto, Compra, DetalleCompra, QR, EncuestaSeatDelivery
        
        models_map = {
            'Usuario': Usuario,
            'Producto': Producto,
            'TipoProducto': TipoProducto,
            'Compra': Compra,
            'DetalleCompra': DetalleCompra,
            'QR': QR,
            'EncuestaSeatDelivery': EncuestaSeatDelivery
        }
        
        model_class = models_map.get(operation['model'])
        if not model_class:
            logger.error(f"Modelo no encontrado: {operation['model']}")
            return False
        
        if operation['type'] == 'delete':
            # DELETE
            cloud_instance = cloud_db.query(model_class).filter_by(**operation['pk_filter']).first()
            if cloud_instance:
                cloud_db.delete(cloud_instance)
                cloud_db.commit()
        else:
            # INSERT o UPDATE
            existing = cloud_db.query(model_class).filter_by(**operation['pk_filter']).first()
            
            if existing:
                # UPDATE
                for key, value in operation['data'].items():
                    setattr(existing, key, value)
            else:
                # INSERT
                new_obj = model_class(**operation['data'])
                cloud_db.add(new_obj)
            
            cloud_db.commit()
        
        cloud_db.close()
        return True
        
    except Exception as e:
        logger.error(f"Error ejecutando operación de sincronización: {e}")
        try:
            cloud_db.close()
        except:
            pass
        return False

def setup_cloud_replication():
    """Configurar la conexión a la base de datos en la nube para replicación"""
    global cloud_engine, CloudSessionLocal, sync_thread, is_syncing
    
    if not config.AUTO_SYNC_TO_CLOUD:
        logger.info("ℹ️  Replicación automática deshabilitada")
        return
    
    if not config.CLOUD_DATABASE_URL:
        logger.warning("⚠️  CLOUD_DATABASE_URL no configurada. Replicación deshabilitada.")
        return
    
    if config.DATABASE_MODE == "cloud":
        logger.info("ℹ️  Ya estás usando la base de datos en la nube directamente")
        return
    
    try:
        logger.info("🔄 Configurando replicación automática a la nube...")
        cloud_engine = create_engine(
            config.CLOUD_DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,  # Reciclar conexiones cada hora
            echo=False
        )
        
        # Probar la conexión
        check_internet_connection()
        
        CloudSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cloud_engine)
        
        # Crear las tablas en la nube si no existen
        if internet_available:
            Base.metadata.create_all(bind=cloud_engine)
            logger.info("✅ Tablas creadas/verificadas en la nube")
        
        # Iniciar thread de sincronización
        if not sync_thread or not sync_thread.is_alive():
            is_syncing = True
            sync_thread = threading.Thread(target=process_sync_queue, daemon=True, name="SyncThread")
            sync_thread.start()
            logger.info("✅ Thread de sincronización iniciado")
        
        logger.info("✅ Replicación automática configurada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error al configurar replicación: {e}")
        logger.info("   La aplicación continuará usando solo la base de datos local")
        cloud_engine = None
        CloudSessionLocal = None

def sync_to_cloud(mapper, connection, target):
    """
    Sincronizar automáticamente los cambios a la base de datos en la nube
    Agrega la operación a una cola para procesamiento asíncrono
    """
    if not CloudSessionLocal:
        return
    
    try:
        # Extraer clave primaria para crear un identificador único
        pk_columns = [col for col in mapper.primary_key]
        if len(pk_columns) == 1:
            pk_name = pk_columns[0].name
            pk_value = getattr(target, pk_name)
            pk_filter = {pk_name: pk_value}
        else:
            pk_filter = {col.name: getattr(target, col.name) for col in pk_columns}
        
        model_name = target.__class__.__name__
        
        # Crear un identificador único para este objeto
        object_id = f"{model_name}:{pk_filter}"
        
        # Evitar duplicados: si ya está siendo sincronizado, skip
        with sync_lock:
            if object_id in syncing_objects:
                return
            syncing_objects.add(object_id)
        
        # Extraer datos del objeto
        data = {}
        for column in mapper.columns:
            value = getattr(target, column.name)
            # Convertir enums a string para serialización
            if hasattr(value, 'value'):
                value = value.value
            data[column.name] = value
        
        # Agregar a la cola
        save_to_sync_queue('insert_update', model_name, data, pk_filter)
        
        # Remover del set después de un tiempo
        def remove_from_syncing():
            time.sleep(2)  # Esperar 2 segundos
            with sync_lock:
                syncing_objects.discard(object_id)
        
        threading.Thread(target=remove_from_syncing, daemon=True).start()
        
    except Exception as e:
        logger.error(f"⚠️  Error al preparar sincronización: {e}")

def sync_delete_to_cloud(mapper, connection, target):
    """
    Sincronizar DELETE a la nube
    Agrega la operación a una cola para procesamiento asíncrono
    """
    if not CloudSessionLocal:
        return
    
    try:
        # Extraer clave primaria
        pk_columns = [col for col in mapper.primary_key]
        
        if len(pk_columns) == 1:
            pk_name = pk_columns[0].name
            pk_value = getattr(target, pk_name)
            pk_filter = {pk_name: pk_value}
        else:
            pk_filter = {col.name: getattr(target, col.name) for col in pk_columns}
        
        model_name = target.__class__.__name__
        
        # Agregar a la cola
        save_to_sync_queue('delete', model_name, None, pk_filter)
        
    except Exception as e:
        logger.error(f"⚠️  Error al preparar DELETE para sincronización: {e}")

def register_sync_events():
    """Registrar eventos para sincronización automática"""
    if not CloudSessionLocal:
        return
    
    from models import Usuario, Producto, TipoProducto, Compra, DetalleCompra, QR, EncuestaSeatDelivery
    
    # Registrar eventos para todas las tablas
    models_to_sync = [Usuario, Producto, TipoProducto, Compra, DetalleCompra, QR, EncuestaSeatDelivery]
    
    for model in models_to_sync:
        event.listen(model, 'after_insert', sync_to_cloud)
        event.listen(model, 'after_update', sync_to_cloud)
        event.listen(model, 'after_delete', sync_delete_to_cloud)
    
    logger.info("✅ Eventos de sincronización registrados")

def get_sync_status():
    """Obtener estado de la sincronización"""
    return {
        'internet_available': internet_available,
        'queue_size': sync_queue.qsize(),
        'sync_thread_alive': sync_thread.is_alive() if sync_thread else False,
        'cloud_configured': CloudSessionLocal is not None
    }

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cloud_db():
    """Dependencia para obtener sesión de la base de datos en la nube (solo lectura)"""
    if not CloudSessionLocal:
        raise Exception("Base de datos en la nube no configurada")
    
    db = CloudSessionLocal()
    try:
        yield db
    finally:
        db.close()
