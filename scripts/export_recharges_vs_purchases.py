"""
Exporta a CSV las métricas por usuario para analizar la relación entre recargas y compras.

Uso:
    python scripts/export_recharges_vs_purchases.py

Columnas:
- user_id
- nombre
- email
- recharge_count (número de recargas)
- recharge_total (valor total recargado)
- purchase_count (número de compras)
- purchase_total (valor total comprado)
- recharge_avg (promedio por recarga)
- purchase_avg (promedio por compra)

Además imprime en consola las correlaciones de Pearson:
- recarga_total vs compra_total
- recarga_total vs cantidad de compras
- cantidad de recargas vs cantidad de compras
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from typing import Iterable, Optional

# Agregar el directorio raíz al path para importar módulos internos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import func

from database import SessionLocal
from models import Compra, RecargaSaldoEvento, Usuario


def pearson(x: Iterable[float], y: Iterable[float]) -> Optional[float]:
    """Calcula la correlación de Pearson; devuelve None si no es calculable."""
    x = list(x)
    y = list(y)
    if len(x) != len(y) or len(x) < 2:
        return None

    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denx = sum((a - mx) ** 2 for a in x) ** 0.5
    deny = sum((b - my) ** 2 for b in y) ** 0.5
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def export_recharges_vs_purchases() -> str:
    """Genera el CSV y retorna la ruta generada."""
    session = SessionLocal()

    try:
        rec_subq = (
            session.query(
                RecargaSaldoEvento.id_usuario.label("user_id"),
                func.count(RecargaSaldoEvento.id).label("recharge_count"),
                func.coalesce(func.sum(RecargaSaldoEvento.monto), 0.0).label(
                    "recharge_total"
                ),
            )
            .group_by(RecargaSaldoEvento.id_usuario)
            .subquery()
        )

        buy_subq = (
            session.query(
                Compra.id_usuario.label("user_id"),
                func.count(Compra.id).label("purchase_count"),
                func.coalesce(func.sum(Compra.total), 0.0).label("purchase_total"),
            )
            .group_by(Compra.id_usuario)
            .subquery()
        )

        query = (
            session.query(
                Usuario.id.label("user_id"),
                Usuario.nombre,
                Usuario.email,
                func.coalesce(rec_subq.c.recharge_count, 0).label("recharge_count"),
                func.coalesce(rec_subq.c.recharge_total, 0.0).label("recharge_total"),
                func.coalesce(buy_subq.c.purchase_count, 0).label("purchase_count"),
                func.coalesce(buy_subq.c.purchase_total, 0.0).label("purchase_total"),
            )
            .outerjoin(rec_subq, rec_subq.c.user_id == Usuario.id)
            .outerjoin(buy_subq, buy_subq.c.user_id == Usuario.id)
            .order_by(Usuario.id)
        )

        rows = query.all()
        if not rows:
            print("⚠️  No hay usuarios para exportar.")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recargas_vs_compras_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "user_id",
                "nombre",
                "email",
                "recharge_count",
                "recharge_total",
                "purchase_count",
                "purchase_total",
                "recharge_avg",
                "purchase_avg",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                recharge_count = int(row.recharge_count or 0)
                purchase_count = int(row.purchase_count or 0)
                recharge_total = float(row.recharge_total or 0.0)
                purchase_total = float(row.purchase_total or 0.0)

                writer.writerow(
                    {
                        "user_id": row.user_id,
                        "nombre": row.nombre,
                        "email": row.email,
                        "recharge_count": recharge_count,
                        "recharge_total": round(recharge_total, 2),
                        "purchase_count": purchase_count,
                        "purchase_total": round(purchase_total, 2),
                        "recharge_avg": round(
                            recharge_total / recharge_count, 2
                        )
                        if recharge_count
                        else 0.0,
                        "purchase_avg": round(
                            purchase_total / purchase_count, 2
                        )
                        if purchase_count
                        else 0.0,
                    }
                )

        # Calcular correlaciones
        rec_total = [float(r.recharge_total or 0.0) for r in rows]
        rec_count = [int(r.recharge_count or 0) for r in rows]
        buy_total = [float(r.purchase_total or 0.0) for r in rows]
        buy_count = [int(r.purchase_count or 0) for r in rows]

        corr_rec_buy_total = pearson(rec_total, buy_total)
        corr_rec_total_buy_count = pearson(rec_total, buy_count)
        corr_rec_count_buy_count = pearson(rec_count, buy_count)

        print(f"✅ CSV generado: {filename}")
        print(f"📁 Ubicación: {os.path.abspath(filename)}")
        print(f"👥 Usuarios exportados: {len(rows)}")
        print("📈 Correlaciones (Pearson):")
        print(f"   recarga_total vs compra_total: {corr_rec_buy_total}")
        print(f"   recarga_total vs cantidad_compras: {corr_rec_total_buy_count}")
        print(f"   cantidad_recargas vs cantidad_compras: {corr_rec_count_buy_count}")
        return filename
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exportar métricas por usuario para analizar recargas vs compras."
    )
    _ = parser.parse_args()

    print("🚀 Exportando correlación recargas/compras...")
    export_recharges_vs_purchases()
    print("✨ Proceso completado.")


if __name__ == "__main__":
    main()
