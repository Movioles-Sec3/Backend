# 📊 Scripts de Utilidad

Esta carpeta contiene scripts auxiliares para gestionar y analizar datos del sistema TapAndToast.

## 📄 `export_compras_tiempos.py`

### Descripción
Exporta todas las compras completadas (estado `ENTREGADO`) con información detallada de sus tiempos a un archivo CSV.

### Uso
```bash
# Desde la raíz del proyecto
python scripts/export_compras_tiempos.py
```

### Salida
El script genera un archivo CSV con el nombre `compras_completadas_YYYYMMDD_HHMMSS.csv` en la raíz del proyecto.

### Columnas del CSV

| Columna | Descripción |
|---------|-------------|
| `id_compra` | ID único de la compra |
| `fecha_creacion` | Fecha y hora cuando se creó la compra |
| `usuario_nombre` | Nombre del usuario que hizo la compra |
| `usuario_email` | Email del usuario |
| `total_cop` | Monto total en pesos colombianos |
| `fecha_en_preparacion` | Timestamp cuando empezó la preparación |
| `fecha_listo` | Timestamp cuando estuvo lista |
| `fecha_entregado` | Timestamp cuando se entregó |
| `tiempo_hasta_preparacion_seg` | Segundos desde creación hasta preparación |
| `tiempo_hasta_preparacion_min` | Minutos desde creación hasta preparación |
| `tiempo_preparacion_seg` | Segundos de duración de la preparación |
| `tiempo_preparacion_min` | Minutos de duración de la preparación |
| `tiempo_espera_entrega_seg` | Segundos desde listo hasta entrega |
| `tiempo_espera_entrega_min` | Minutos desde listo hasta entrega |
| `tiempo_total_seg` | Segundos totales del proceso |
| `tiempo_total_min` | Minutos totales del proceso |

### Ejemplo de salida en consola
```
🚀 Exportando compras completadas con tiempos...

✅ CSV generado exitosamente: compras_completadas_20251004_153045.csv
📊 Total de compras exportadas: 25
📁 Ubicación: C:\...\Backend\compras_completadas_20251004_153045.csv

📈 Estadísticas:
   Tiempo promedio total: 17.5 minutos
   Tiempo mínimo: 8.2 minutos
   Tiempo máximo: 35.7 minutos

✨ Proceso completado!
```

### Casos de uso
- **Análisis de rendimiento**: Identificar cuellos de botella en el proceso
- **Reportes gerenciales**: Estadísticas de tiempos de servicio
- **Optimización**: Detectar patrones para mejorar eficiencia
- **KPIs**: Seguimiento de métricas clave de servicio

### Requisitos
- Base de datos con compras en estado `ENTREGADO`
- Permisos de escritura en el directorio actual

### Notas
- Solo exporta compras completadas (estado `ENTREGADO`)
- Los tiempos se calculan en tiempo de ejecución
- Si una compra no tiene todos los timestamps, mostrará `N/A` en esos campos
- El archivo se genera con timestamp para evitar sobrescribir exports anteriores

