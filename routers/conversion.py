from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from services.currency_service import convert_currency, get_supported_currencies

router = APIRouter(prefix="/conversiones", tags=["conversiones"])

@router.get("/")
def convertir_moneda(
    monto: float = Query(..., description="Monto a convertir", gt=0),
    moneda_origen: str = Query("COP", description="Moneda de origen (código ISO)", max_length=3),
    moneda_destino: Optional[str] = Query(None, description="Moneda destino específica (opcional)", max_length=3)
):
    """
    Convierte un monto de una moneda a otra(s).
    
    Si no se especifica `moneda_destino`, retorna conversiones a las principales monedas.
    Si se especifica `moneda_destino`, retorna solo esa conversión.
    
    **Ejemplo de uso:**
    - `/conversiones?monto=15000&moneda_origen=COP` → Conversión a varias monedas
    - `/conversiones?monto=15000&moneda_origen=COP&moneda_destino=USD` → Solo a USD
    
    **Monedas principales soportadas:**
    - COP - Peso colombiano
    - USD - Dólar estadounidense
    - EUR - Euro
    - GBP - Libra esterlina
    - MXN - Peso mexicano
    - BRL - Real brasileño
    - ARS - Peso argentino
    - CLP - Peso chileno
    
    **Nota:** Las tasas se actualizan cada hora y se cachean para mejorar el rendimiento.
    """
    try:
        resultado = convert_currency(monto, moneda_origen.upper(), moneda_destino.upper() if moneda_destino else None)
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tasas de cambio: {str(e)}"
        )

@router.get("/monedas")
def listar_monedas_soportadas():
    """
    Obtiene la lista completa de monedas soportadas por el sistema.
    
    Retorna más de 160 códigos de moneda ISO 4217.
    """
    try:
        monedas = get_supported_currencies()
        return {
            "total": len(monedas),
            "monedas": monedas,
            "principales": ["COP", "USD", "EUR", "GBP", "MXN", "BRL", "ARS", "CLP"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener monedas soportadas: {str(e)}"
        )

