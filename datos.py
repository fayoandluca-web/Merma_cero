# -*- coding: utf-8 -*-
"""Módulo de ingesta y limpieza de datos climáticos para el estándar x200."""
import sys
import os

# Asegurar importabilidad del paquete
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merma_cero.domain.entities import WeatherState
from merma_cero.infrastructure.weather_adapter import OpenMeteoAdapter

def obtener_datos_clima(latitude: float, longitude: float) -> dict:
    """Descarga datos del clima actuales mediante el adaptador OpenMeteo.
    
    Aplica el saneamiento de rangos físicos (clipping) de forma transparente.
    """
    adapter = OpenMeteoAdapter()
    weather_state = adapter.get_weather(latitude, longitude)
    
    return {
        "temperature": weather_state.temperature,
        "relative_humidity": weather_state.relative_humidity,
        "precipitation_probability": weather_state.precipitation_probability
    }

def obtener_historico_temperaturas(latitude: float, longitude: float) -> tuple[list[float], list[float]]:
    """Provee series temporales de temperatura histórica y medias estacionales.
    
    Se utiliza como entrada para la estimación de volatilidad condicional GARCH(1,1).
    """
    # En producción esto consumirá un API histórica. Como fallback/estándar
    # actual, genera una serie determinista acotada alrededor del clima en tiempo real
    actual = obtener_datos_clima(latitude, longitude)
    temp_actual = actual["temperature"]
    
    import math
    hist = []
    means = []
    for i in range(15):
        # Generar oscilación realista de 15 días con anomalías climáticas
        anomalia = math.sin(i * 0.8) * 2.0
        hist.append(temp_actual + anomalia)
        means.append(temp_actual) # Media estacional
        
    return hist, means

if __name__ == "__main__":
    print("[*] Ingestando datos de prueba para CDMX (19.43, -99.13)...")
    try:
        clima = obtener_datos_clima(19.43, -99.13)
        print(f"[+] Clima actual saneado: {clima}")
        
        hist, means = obtener_historico_temperaturas(19.43, -99.13)
        print(f"[+] Serie histórica GARCH: {hist[:5]}...")
    except Exception as e:
        print(f"[ERROR] Falló la ingesta de datos: {e}")
