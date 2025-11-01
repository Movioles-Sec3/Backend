"""
Exporta métricas de popularidad por producto a un archivo CSV.

Uso:
    python scripts/export_product_popularity.py [--limit N]

Columnas incluidas:
- product_id
- product_name
- total_orders (número de compras distintas)
- total_units (sumatoria de unidades vendidas)
- total_revenue (en la moneda registrada)
- first_order_at
- last_order_at
"""

import sys
import os
import csv
from datetime import datetime
from typing import Optional
import argparse

# Agregar el directorio raíz al path para importar módulos internos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import func, desc

from database import SessionLocal
from models import Compra, DetalleCompra, Producto, EstadoCompra


def export_product_popularity(limit: Optional[int] = None) -> str:
    """Genera el CSV con métricas de productos y devuelve la ruta generada."""
    session = SessionLocal()

    try:
        query = (
            session.query(
                Producto.id.label("product_id"),
                Producto.nombre.label("product_name"),
                func.count(func.distinct(DetalleCompra.id_compra)).label("total_orders"),
                func.coalesce(func.sum(DetalleCompra.cantidad), 0).label("total_units"),
                func.coalesce(
                    func.sum(DetalleCompra.cantidad * DetalleCompra.precio_unitario_compra),
                    0.0,
                ).label("total_revenue"),
                func.min(Compra.fecha_hora).label("first_order_at"),
                func.max(Compra.fecha_hora).label("last_order_at"),
            )
            .join(DetalleCompra, DetalleCompra.id_producto == Producto.id)
            .join(Compra, Compra.id == DetalleCompra.id_compra)
            .filter(Compra.estado == EstadoCompra.ENTREGADO)
            .group_by(Producto.id, Producto.nombre)
            .order_by(desc("total_units"), desc("total_orders"))
        )

        if limit:
            query = query.limit(limit)

        rows = query.all()

        if not rows:
            print("⚠️  No hay compras entregadas para calcular popularidad.")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"productos_populares_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "product_id",
                "product_name",
                "total_orders",
                "total_units",
                "total_revenue",
                "first_order_at",
                "last_order_at",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                writer.writerow(
                    {
                        "product_id": row.product_id,
                        "product_name": row.product_name,
                        "total_orders": row.total_orders,
                        "total_units": row.total_units,
                        "total_revenue": round(row.total_revenue, 2),
                        "first_order_at": row.first_order_at.strftime("%Y-%m-%d %H:%M:%S")
                        if row.first_order_at
                        else "N/A",
                        "last_order_at": row.last_order_at.strftime("%Y-%m-%d %H:%M:%S")
                        if row.last_order_at
                        else "N/A",
                    }
                )

        print(f"✅ CSV generado: {filename}")
        print(f"📁 Ubicación: {os.path.abspath(filename)}")
        print(f"📊 Productos incluidos: {len(rows)}")
        return filename
    except Exception as exc:
        print(f"❌ Error al exportar popularidad: {exc}")
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Exportar productos más pedidos a CSV.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limitar la cantidad de productos exportados (opcional).",
    )
    args = parser.parse_args()

    print("🚀 Exportando métricas de productos...")
    export_product_popularity(limit=args.limit)
    print("\n✨ Proceso completado.")


if __name__ == "__main__":
    main()
