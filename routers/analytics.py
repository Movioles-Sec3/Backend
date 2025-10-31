from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Compra, DetalleCompra, Producto, TipoProducto, EstadoCompra
from schemas import (
    ReordersByCategoryResponse,
    CategoryReorderStats,
    CategoryReorderHourCount,
    OrderPeakHoursResponse,
    HourlyDistribution,
    OrderPeakHoursSummary,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/reorders-by-category", response_model=ReordersByCategoryResponse)
def reorders_by_category(
    start: Optional[datetime] = Query(None, description="Start datetime (inclusive) in UTC"),
    end: Optional[datetime] = Query(None, description="End datetime (exclusive) in UTC"),
    timezone_offset_minutes: int = Query(0, description="Client timezone offset from UTC in minutes (e.g., -300 for UTC-5)"),
    db: Session = Depends(get_db)
):
    """
    Devuelve qué categorías se reordenan con más frecuencia y en qué horas del día.

    Definición de "reorder": Una compra que incluye al menos un producto de una categoría
    que el mismo usuario ya compró antes (en cualquier evento anterior al rango actual).
    Si un carrito incluye múltiples productos de la misma categoría, cuenta como 1 "reorder" para esa categoría.
    """
    # Determinar ventana por defecto (últimos 30 días) si no se provee
    now_utc = datetime.utcnow()
    if end is None:
        end = now_utc
    if start is None:
        start = end - timedelta(days=30)

    # Subconsulta: compras en el rango, entregadas o al menos pagadas (consideramos eventos reales)
    compras_q = (
        db.query(Compra.id, Compra.id_usuario, Compra.fecha_hora)
        .filter(Compra.fecha_hora >= start, Compra.fecha_hora < end)
        .filter(Compra.estado.in_([EstadoCompra.PAGADO, EstadoCompra.EN_PREPARACION, EstadoCompra.LISTO, EstadoCompra.ENTREGADO]))
        .subquery()
    )

    # Detalles con categoría por compra
    detalles_q = (
        db.query(
            compras_q.c.id.label("compra_id"),
            compras_q.c.id_usuario.label("usuario_id"),
            compras_q.c.fecha_hora.label("fecha_hora"),
            TipoProducto.id.label("categoria_id"),
            TipoProducto.nombre.label("categoria_nombre"),
        )
        .join(DetalleCompra, DetalleCompra.id_compra == compras_q.c.id)
        .join(Producto, Producto.id == DetalleCompra.id_producto)
        .join(TipoProducto, TipoProducto.id == Producto.id_tipo)
        .subquery()
    )

    # Para cada compra-categoria, determinar si es "reorder" vs primera vez para ese usuario
    # Un reorder ocurre si existe alguna compra anterior del mismo usuario con la misma categoria antes de "fecha_hora"
    # Nota: Para SQLite, correlacionar con subqueries simples
    rows = db.query(
        detalles_q.c.compra_id,
        detalles_q.c.usuario_id,
        detalles_q.c.fecha_hora,
        detalles_q.c.categoria_id,
        detalles_q.c.categoria_nombre,
    ).all()

    # Pre-cargar historial previo por (usuario, categoria) con fecha < start y también dentro del rango
    historial_prev = set()  # pares (usuario_id, categoria_id) con historial antes del rango
    # Buscar compras anteriores al inicio para clasificar correctamente reorders al principio del rango
    prev_q = (
        db.query(TipoProducto.id.label("categoria_id"), Compra.id_usuario.label("usuario_id"))
        .join(Producto, Producto.id_tipo == TipoProducto.id)
        .join(DetalleCompra, DetalleCompra.id_producto == Producto.id)
        .join(Compra, Compra.id == DetalleCompra.id_compra)
        .filter(Compra.fecha_hora < start)
        .distinct()
    )
    for c_id, u_id in prev_q.all():
        historial_prev.add((u_id, c_id))

    # Ordenar filas por fecha para evaluar primer/segundo etc. dentro del rango
    rows_sorted = sorted(rows, key=lambda r: (r.usuario_id, r.categoria_id, r.fecha_hora, r.compra_id))

    # Para tracking dentro del rango: si el usuario ya ordenó esa categoría previamente en el rango
    seen_in_range: Dict[Tuple[int, int], bool] = {}

    # Acumuladores por categoría
    reorder_count: Dict[int, int] = {}
    category_name: Dict[int, str] = {}
    hour_distribution: Dict[int, Dict[int, int]] = {}

    def to_local_hour(dt: datetime, offset_min: int) -> int:
        return ((dt + timedelta(minutes=offset_min)).hour) % 24

    # Reducir por compra_id-categoria para no contar múltiples productos de la misma categoría en una compra
    unique_keys = set()
    for r in rows_sorted:
        key = (r.compra_id, r.categoria_id)
        if key in unique_keys:
            continue
        unique_keys.add(key)

        cat_id = r.categoria_id
        category_name[cat_id] = r.categoria_nombre

        user_cat = (r.usuario_id, cat_id)
        already_had = user_cat in historial_prev or seen_in_range.get(user_cat, False)
        # Marcar seen para compras posteriores dentro del rango
        seen_in_range[user_cat] = True

        if already_had:
            reorder_count[cat_id] = reorder_count.get(cat_id, 0) + 1
            hour = to_local_hour(r.fecha_hora, timezone_offset_minutes)
            if cat_id not in hour_distribution:
                hour_distribution[cat_id] = {}
            hour_distribution[cat_id][hour] = hour_distribution[cat_id].get(hour, 0) + 1

    # Construir respuesta
    categories: List[CategoryReorderStats] = []
    for cat_id, count in sorted(reorder_count.items(), key=lambda x: x[1], reverse=True):
        hour_counts_map = hour_distribution.get(cat_id, {})
        hour_counts = [
            CategoryReorderHourCount(hour=h, count=c) for h, c in sorted(hour_counts_map.items())
        ]
        # Peak hours: horas con el máximo valor
        if hour_counts:
            max_c = max(hc.count for hc in hour_counts)
            peaks = [hc.hour for hc in hour_counts if hc.count == max_c]
        else:
            peaks = []
        categories.append(
            CategoryReorderStats(
                categoria_id=cat_id,
                categoria_nombre=category_name.get(cat_id, str(cat_id)),
                reorder_count=count,
                hour_distribution=hour_counts,
                peak_hours=peaks,
            )
        )

    return ReordersByCategoryResponse(
        start=start,
        end=end,
        timezone_offset_minutes=timezone_offset_minutes,
        categories=categories,
    )


@router.get("/order-peak-hours", response_model=OrderPeakHoursResponse)
def order_peak_hours(
    start: Optional[datetime] = Query(None, description="Start datetime (inclusive) in UTC"),
    end: Optional[datetime] = Query(None, description="End datetime (exclusive) in UTC"),
    timezone_offset_minutes: int = Query(0, description="Client timezone offset from UTC in minutes (e.g., -300 for UTC-5)"),
    db: Session = Depends(get_db)
):
    """
    Analiza las horas pico de pedidos para identificar patrones de volumen de órdenes durante el día.
    
    Retorna:
    - Distribución horaria de pedidos con conteo, ingresos totales y valor promedio
    - Identificación de horas pico (top 25% por volumen)
    - Estadísticas resumidas incluyendo hora más ocupada y más tranquila
    """
    # Determinar ventana por defecto (día actual) si no se provee
    now_utc = datetime.utcnow()
    if end is None:
        end = now_utc
    if start is None:
        # Default to start of current day
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Query de compras en el rango con estados válidos (al menos pagadas)
    compras = (
        db.query(
            Compra.id,
            Compra.fecha_hora,
            Compra.total
        )
        .filter(Compra.fecha_hora >= start, Compra.fecha_hora < end)
        .filter(Compra.estado.in_([
            EstadoCompra.PAGADO,
            EstadoCompra.EN_PREPARACION,
            EstadoCompra.LISTO,
            EstadoCompra.ENTREGADO
        ]))
        .all()
    )
    
    # Convertir a hora local y agrupar por hora
    def to_local_hour(dt: datetime, offset_min: int) -> int:
        return ((dt + timedelta(minutes=offset_min)).hour) % 24
    
    # Agrupar por hora
    hourly_data: Dict[int, List[float]] = {h: [] for h in range(24)}
    
    for compra in compras:
        hour = to_local_hour(compra.fecha_hora, timezone_offset_minutes)
        hourly_data[hour].append(compra.total)
    
    # Calcular estadísticas por hora
    hourly_stats = []
    total_orders = len(compras)
    
    for hour in range(24):
        orders = hourly_data[hour]
        order_count = len(orders)
        total_revenue = sum(orders)
        avg_order_value = total_revenue / order_count if order_count > 0 else 0.0
        percentage = (order_count / total_orders * 100) if total_orders > 0 else 0.0
        
        hourly_stats.append({
            'hour': hour,
            'order_count': order_count,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'percentage': round(percentage, 2)
        })
    
    # Identificar horas pico (top 25% por volumen)
    if hourly_stats:
        order_counts = [h['order_count'] for h in hourly_stats]
        threshold = sorted(order_counts, reverse=True)[int(len(order_counts) * 0.25)] if order_counts else 0
        
        peak_hours = []
        for h in hourly_stats:
            is_peak = h['order_count'] >= threshold and h['order_count'] > 0
            h['is_peak'] = is_peak
            if is_peak:
                peak_hours.append(h['hour'])
    else:
        peak_hours = []
        for h in hourly_stats:
            h['is_peak'] = False
    
    # Crear lista de distribución horaria
    hourly_distribution = [
        HourlyDistribution(
            hour=h['hour'],
            order_count=h['order_count'],
            total_revenue=h['total_revenue'],
            avg_order_value=h['avg_order_value'],
            percentage=h['percentage'],
            is_peak=h['is_peak']
        )
        for h in hourly_stats
    ]
    
    # Calcular estadísticas de resumen
    if total_orders > 0:
        orders_in_peak_hours = sum(h['order_count'] for h in hourly_stats if h['is_peak'])
        percentage_in_peak = (orders_in_peak_hours / total_orders * 100) if total_orders > 0 else 0.0
        
        # Encontrar hora más ocupada y más tranquila
        busiest = max(hourly_stats, key=lambda h: h['order_count'])
        slowest = min(hourly_stats, key=lambda h: h['order_count'])
        
        peak_hour_range = f"{min(peak_hours)}:00 - {max(peak_hours)}:00" if peak_hours else "N/A"
        
        summary = OrderPeakHoursSummary(
            total_orders=total_orders,
            peak_hours=peak_hours,
            peak_hour_range=peak_hour_range,
            orders_in_peak_hours=orders_in_peak_hours,
            percentage_in_peak_hours=round(percentage_in_peak, 1),
            busiest_hour=busiest['hour'],
            busiest_hour_orders=busiest['order_count'],
            slowest_hour=slowest['hour'],
            slowest_hour_orders=slowest['order_count']
        )
    else:
        # Sin datos, retornar valores por defecto
        summary = OrderPeakHoursSummary(
            total_orders=0,
            peak_hours=[],
            peak_hour_range="N/A",
            orders_in_peak_hours=0,
            percentage_in_peak_hours=0.0,
            busiest_hour=0,
            busiest_hour_orders=0,
            slowest_hour=0,
            slowest_hour_orders=0
        )
    
    return OrderPeakHoursResponse(
        start=start,
        end=end,
        timezone_offset_minutes=timezone_offset_minutes,
        hourly_distribution=hourly_distribution,
        peak_hours=peak_hours,
        summary=summary
    )



