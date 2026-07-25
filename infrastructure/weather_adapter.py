# -*- coding: utf-8 -*-
"""Adaptador de clima resiliente con fallback multinivel usando urllib estándar (Zero-Dependencies)."""
import urllib.request
import json
import time
import math
from typing import Dict, Tuple
from merma_cero.domain.entities import WeatherState
from merma_cero.application.ports import WeatherPort

class OpenMeteoAdapter(WeatherPort):
    """Adaptador para consultar Open-Meteo con resiliencia total ante caídas de red."""

    def __init__(self):
        # Caché en memoria: geocerca de cuadricula (redondeada a 2 decimales ~1km) -> (timestamp, WeatherState)
        self._cache: Dict[Tuple[float, float], Tuple[float, WeatherState]] = {}
        self.cache_ttl = 10800  # 3 horas de validez en segundos

    def get_weather(self, lat: float, lon: float) -> WeatherState:
        """Consulta el clima georreferenciado con failover multinivel.
        
        Flujo de Resiliencia:
            1. Petición HTTP a Open-Meteo con timeout de 1.5 segundos.
            2. Si falla: busca en la caché en memoria georreferenciada.
            3. Si no hay caché: genera una aproximación climatológica matemática basada en la fecha y latitud.
        """
        # Redondear coordenadas para cachear por vecindario (~1.1 km) y reducir llamadas a API
        lat_grid = round(lat, 2)
        lon_grid = round(lon, 2)
        grid_key = (lat_grid, lon_grid)
        now = time.time()

        # 1. Petición HTTP activa
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,precipitation_probability&"
            f"forecast_days=1"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MermaCeroOracle/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                
            current = payload["current"]
            # Open-Meteo retorna humedad en % [0, 100] y probabilidad en % [0, 100]
            # Convertimos a fracción para que coincida con las validaciones de frontera
            weather = WeatherState(
                temperature=float(current["temperature_2m"]),
                relative_humidity=float(current["relative_humidity_2m"]) / 100.0,
                precipitation_probability=float(current["precipitation_probability"]) / 100.0
            )
            # Actualizar caché
            self._cache[grid_key] = (now, weather)
            return weather

        except Exception:
            # 2. Primer Nivel de Fallback: Buscar en Caché local si es menor a TTL
            if grid_key in self._cache:
                timestamp, cached_weather = self._cache[grid_key]
                if now - timestamp < self.cache_ttl:
                    return cached_weather

            # 3. Segundo Nivel de Fallback: Generador Climatológico Determinista (Murphy Law)
            return self._calculate_climatological_fallback(lat, now)

    def _calculate_climatological_fallback(self, lat: float, now: float) -> WeatherState:
        """Aproximación matemática del clima local según latitud y estación del año."""
        # Obtener el día del año (0 a 365)
        local_struct = time.localtime(now)
        day_of_year = local_struct.tm_yday
        month = local_struct.tm_mon

        # Ecuación sinusoidal para simular temperatura estacional
        # En el hemisferio norte el pico es en julio (~día 200), en el sur es invertido
        is_northern_hemisphere = lat >= 0
        phase = 200 if is_northern_hemisphere else 20
        
        # Temperatura promedio base según distancia al ecuador (latitud)
        # Ecuador lat=0 es ~28°C promedio, Polos lat=90 es ~ -10°C
        base_temp = 28.0 - 0.4 * abs(lat)
        amplitude = 6.0 if abs(lat) > 15.0 else 2.0  # Las zonas templadas tienen mayor variación estacional
        
        season_mod = math.cos(2 * math.pi * (day_of_year - phase) / 365.0)
        estimated_temp = base_temp + amplitude * season_mod

        # Modelado básico de lluvia estacional (ej. época de huracanes / lluvias Jun-Oct en MX)
        # Humedad relativa alta en verano
        if month in [6, 7, 8, 9]:
            humidity = 0.75
            rain_prob = 0.50 if is_northern_hemisphere else 0.15
        else:
            humidity = 0.50
            rain_prob = 0.10

        return WeatherState(
            temperature=float(estimated_temp),
            relative_humidity=float(humidity),
            precipitation_probability=float(rain_prob)
        )
