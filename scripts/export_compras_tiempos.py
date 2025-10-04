"""
Script para exportar compras completadas con sus tiempos a un archivo CSV.

Uso:
    python scripts/export_compras_tiempos.py

Genera un archivo CSV con:
- ID de la compra
- Fecha y hora de creación
- Usuario (nombre y email)
- Total de la compra
- Timestamps de cada etapa
- Tiempos calculados (en segundos y minutos)
"""

import sys
import os
from datetime import datetime
import csv

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal
from models import Compra, Usuario, EstadoCompra


def calcular_tiempo(fecha_inicio, fecha_fin):
    """Calcula la diferencia en segundos entre dos fechas"""
    if fecha_inicio and fecha_fin:
        return (fecha_fin - fecha_inicio).total_seconds()
    return None


def segundos_a_minutos(segundos):
    """Convierte segundos a minutos (formato: X.XX min)"""
    if segundos is not None:
        return round(segundos / 60, 2)
    return None


def export_compras_completadas():
    """Exporta las compras completadas con sus tiempos a un archivo CSV"""
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Consultar compras con estado ENTREGADO
        compras = db.query(Compra).filter(
            Compra.estado == EstadoCompra.ENTREGADO
        ).order_by(Compra.fecha_hora.desc()).all()
        
        if not compras:
            print("⚠️  No hay compras completadas en la base de datos.")
            return
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compras_completadas_{timestamp}.csv"
        
        # Escribir CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id_compra',
                'fecha_creacion',
                'usuario_nombre',
                'usuario_email',
                'total_cop',
                'fecha_en_preparacion',
                'fecha_listo',
                'fecha_entregado',
                'tiempo_hasta_preparacion_seg',
                'tiempo_hasta_preparacion_min',
                'tiempo_preparacion_seg',
                'tiempo_preparacion_min',
                'tiempo_espera_entrega_seg',
                'tiempo_espera_entrega_min',
                'tiempo_total_seg',
                'tiempo_total_min'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Procesar cada compra
            for compra in compras:
                # Calcular tiempos
                tiempo_hasta_prep = calcular_tiempo(compra.fecha_hora, compra.fecha_en_preparacion)
                tiempo_prep = calcular_tiempo(compra.fecha_en_preparacion, compra.fecha_listo)
                tiempo_espera = calcular_tiempo(compra.fecha_listo, compra.fecha_entregado)
                tiempo_total = calcular_tiempo(compra.fecha_hora, compra.fecha_entregado)
                
                # Escribir fila
                writer.writerow({
                    'id_compra': compra.id,
                    'fecha_creacion': compra.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
                    'usuario_nombre': compra.usuario.nombre,
                    'usuario_email': compra.usuario.email,
                    'total_cop': compra.total,
                    'fecha_en_preparacion': compra.fecha_en_preparacion.strftime('%Y-%m-%d %H:%M:%S') if compra.fecha_en_preparacion else 'N/A',
                    'fecha_listo': compra.fecha_listo.strftime('%Y-%m-%d %H:%M:%S') if compra.fecha_listo else 'N/A',
                    'fecha_entregado': compra.fecha_entregado.strftime('%Y-%m-%d %H:%M:%S') if compra.fecha_entregado else 'N/A',
                    'tiempo_hasta_preparacion_seg': tiempo_hasta_prep if tiempo_hasta_prep else 'N/A',
                    'tiempo_hasta_preparacion_min': segundos_a_minutos(tiempo_hasta_prep) if tiempo_hasta_prep else 'N/A',
                    'tiempo_preparacion_seg': tiempo_prep if tiempo_prep else 'N/A',
                    'tiempo_preparacion_min': segundos_a_minutos(tiempo_prep) if tiempo_prep else 'N/A',
                    'tiempo_espera_entrega_seg': tiempo_espera if tiempo_espera else 'N/A',
                    'tiempo_espera_entrega_min': segundos_a_minutos(tiempo_espera) if tiempo_espera else 'N/A',
                    'tiempo_total_seg': tiempo_total if tiempo_total else 'N/A',
                    'tiempo_total_min': segundos_a_minutos(tiempo_total) if tiempo_total else 'N/A'
                })
        
        print(f"✅ CSV generado exitosamente: {filename}")
        print(f"📊 Total de compras exportadas: {len(compras)}")
        print(f"📁 Ubicación: {os.path.abspath(filename)}")
        
        # Mostrar estadísticas rápidas
        tiempos_totales = [calcular_tiempo(c.fecha_hora, c.fecha_entregado) for c in compras]
        tiempos_totales = [t for t in tiempos_totales if t is not None]
        
        if tiempos_totales:
            promedio = sum(tiempos_totales) / len(tiempos_totales)
            print(f"\n📈 Estadísticas:")
            print(f"   Tiempo promedio total: {segundos_a_minutos(promedio)} minutos")
            print(f"   Tiempo mínimo: {segundos_a_minutos(min(tiempos_totales))} minutos")
            print(f"   Tiempo máximo: {segundos_a_minutos(max(tiempos_totales))} minutos")
        
    except Exception as e:
        print(f"❌ Error al exportar compras: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Exportando compras completadas con tiempos...\n")
    export_compras_completadas()
    print("\n✨ Proceso completado!")

