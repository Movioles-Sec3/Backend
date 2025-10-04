import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}"

# Cache simple para las tasas (evitar llamadas innecesarias)
_cache = {
    "rates": None,
    "last_update": None,
    "cache_duration": timedelta(hours=1)  # Cachear por 1 hora
}

def _fetch_exchange_rates(base_currency: str = "COP") -> Dict:
    """
    Obtiene las tasas de cambio desde la API.
    Usa cache para evitar llamadas excesivas.
    """
    # Verificar si hay cache válido
    if (_cache["rates"] is not None and 
        _cache["last_update"] is not None and 
        datetime.now() - _cache["last_update"] < _cache["cache_duration"]):
        return _cache["rates"]
    
    # Hacer llamada a la API
    try:
        response = requests.get(f"{BASE_URL}/latest/{base_currency}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("result") == "success":
            # Actualizar cache
            _cache["rates"] = data["conversion_rates"]
            _cache["last_update"] = datetime.now()
            return data["conversion_rates"]
        else:
            raise Exception(f"Error en la API: {data.get('error-type', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al consultar la API de tasas de cambio: {str(e)}")

def convert_currency(
    amount: float, 
    from_currency: str = "COP", 
    to_currency: Optional[str] = None
) -> Dict:
    """
    Convierte un monto de una moneda a otra(s).
    
    Args:
        amount: Monto a convertir
        from_currency: Moneda origen (default: COP)
        to_currency: Moneda destino (opcional). Si es None, retorna todas las principales.
    
    Returns:
        Dict con las conversiones
    """
    # Obtener tasas de cambio
    rates = _fetch_exchange_rates(from_currency)
    
    # Si se especifica una moneda destino específica
    if to_currency:
        if to_currency.upper() not in rates:
            raise ValueError(f"Moneda '{to_currency}' no soportada")
        
        converted_amount = amount * rates[to_currency.upper()]
        return {
            "monto_original": amount,
            "moneda_origen": from_currency.upper(),
            "monto_convertido": round(converted_amount, 2),
            "moneda_destino": to_currency.upper(),
            "tasa_cambio": rates[to_currency.upper()],
            "fecha_actualizacion": _cache["last_update"].isoformat() if _cache["last_update"] else None
        }
    
    # Si no se especifica, retornar conversiones a monedas principales
    principales = ["USD", "EUR", "GBP", "MXN", "BRL", "ARS", "CLP"]
    conversiones = {}
    
    for currency in principales:
        if currency in rates:
            conversiones[currency] = round(amount * rates[currency], 2)
    
    return {
        "monto_original": amount,
        "moneda_origen": from_currency.upper(),
        "conversiones": conversiones,
        "fecha_actualizacion": _cache["last_update"].isoformat() if _cache["last_update"] else None
    }

def get_supported_currencies() -> list:
    """
    Retorna la lista de monedas soportadas.
    """
    rates = _fetch_exchange_rates()
    return sorted(list(rates.keys()))

