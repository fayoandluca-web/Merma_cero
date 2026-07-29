# -*- coding: utf-8 -*-
"""Módulo de siembra (seeding) optimizado para inicializar la base de datos de Merma Cero."""

import os
import sys
import time
import json
import random
import math
import datetime
from typing import List, Tuple, Dict, Any

from merma_cero.domain.entities import Vendor, WeatherState
from merma_cero.domain.models import DecayKinetics, KellyMermaSizer
from merma_cero.config import INVENTORY_PARAMETERS
from merma_cero.application.ports import VendorRepositoryPort
from merma_cero.infrastructure.sqlite_repository import SQLiteVendorRepository


def _log_seeder(severity: str, message: str, context: Dict[str, Any] = None) -> None:
    """Escribe un log estructurado JSON en stderr siguiendo el estándar de rigor_lenguaje.md."""
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "severity": severity,
        "trace_id": "seeder-init",
        "module": "merma_cero.infrastructure.seeder",
        "message": message,
        "context": context or {}
    }
    sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    sys.stderr.flush()


def seed_database(repo: VendorRepositoryPort) -> None:
    """Genera 1000 vendedores realistas en la base de datos si esta se encuentra vacía."""
    
    # 1. Comprobar si la base de datos ya contiene registros de forma ultra-rápida.
    is_empty = False
    if isinstance(repo, SQLiteVendorRepository):
        # Conexión directa y rápida a la base de datos SQLite para evitar cargar todo
        conn = repo._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vendors")
            total_count: int = cursor.fetchone()[0]
            
            count_default = 0
            if total_count >= 10:
                try:
                    cursor.execute("SELECT COUNT(*) FROM vendors WHERE address = 'Colima, México'")
                    count_default = cursor.fetchone()[0]
                except Exception:
                    pass
            is_empty = (total_count < 10 or count_default > 900)
        except Exception:
            # Si hay algún problema, por ejemplo, que la tabla no esté inicializada
            is_empty = True
        finally:
            conn.close()
    else:
        # Fallback para otros repositorios (ej. JSONVendorRepository)
        try:
            all_vendors = repo.get_all()
            total_count = len(all_vendors)
            count_default = sum(1 for v in all_vendors if getattr(v, "address", "") == "Colima, México")
            is_empty = (total_count < 10 or count_default > 900)
        except Exception:
            is_empty = True

    if not is_empty:
        _log_seeder("INFO", "La base de datos ya contiene registros. Omitiendo proceso de siembra.")
        return

    _log_seeder("INFO", "La base de datos está vacía. Iniciando generación de 1000 vendedores realistas.")

    # Definición de mercados representativos en México
    MARKETS: List[Dict[str, Any]] = [
        # Colima
        {"name": "Villa de Álvarez, Colima", "lat": 19.266, "lon": -103.739},
        {"name": "Mezcalito, Colima", "lat": 19.242, "lon": -103.723},
        {"name": "Placetas, Colima", "lat": 19.249, "lon": -103.737},
        # CDMX
        {"name": "Central de Abasto, CDMX", "lat": 19.372, "lon": -99.090},
        {"name": "Tepito, CDMX", "lat": 19.444, "lon": -99.127},
        {"name": "La Merced, CDMX", "lat": 19.425, "lon": -99.125},
        # Guadalajara
        {"name": "El Baratillo, Guadalajara", "lat": 20.679, "lon": -103.318},
        # Monterrey
        {"name": "Mercado Juárez, Monterrey", "lat": 25.685, "lon": -100.312},
        {"name": "Mercado Estrella, Monterrey", "lat": 25.723, "lon": -100.320}
    ]

    categories: List[str] = ["seafood", "flowers", "fruit_vegetables", "dairy", "generic"]

    # Diccionarios de plantillas de mensajes y tips
    queries_by_category: Dict[str, List[str]] = {
        "seafood": [
            "vendo camaron en el mercado",
            "me das el pronostico de hoy para pescado",
            "hola, vendo mariscos",
            "quiero saber la merma de mi pescado",
            "cuanta merma de pulpo tendre hoy?"
        ],
        "flowers": [
            "tengo rosas para vender hoy",
            "cuanto va a durar mi arreglo de flores?",
            "vendo claveles y rosas",
            "pronostico flores",
            "hola, vendo flores"
        ],
        "fruit_vegetables": [
            "tengo jitomates y aguacates",
            "vendo platano y limon en el mercado",
            "cuanto dura mi fruta con este calor?",
            "pronostico de verduras",
            "tengo verduras para vender"
        ],
        "dairy": [
            "vendo quesos y crema en el tianguis",
            "pronostico para quesos",
            "hola, vendo lacteos",
            "se va a echar a perder mi queso hoy?",
            "cuanto queso compro hoy?"
        ],
        "generic": [
            "hola, vendo mercancia general",
            "pronostico de hoy",
            "quiero saber la merma de mis productos",
            "recomiendame cuanto comprar hoy",
            "vendo cosas variadas"
        ]
    }

    tips_by_category: Dict[str, str] = {
        "seafood": "Mantener en abundante hielo triturado. Evitar exposición directa al sol. Desechar si detecta mal olor.",
        "flowers": "Cortar tallos en diagonal. Colocar en agua limpia y fresca. Rociar pétalos con atomizador fino.",
        "fruit_vegetables": "Separar plátanos y tomates maduros. Almacenar en cajas ventiladas. Tapar con mantas húmedas.",
        "dairy": "Conservar en hielera cerrada con congelantes. Evitar abrir constantemente. Controlar temperatura.",
        "generic": "Colocar en tarimas elevadas del suelo. Evitar humedad directa. Mantener ventilación constante."
    }

    # Fijar semilla aleatoria para reproducibilidad y estabilidad estocástica
    random.seed(1337)

    now_ts: float = time.time()
    data_to_insert: List[Tuple[Any, ...]] = []

    for i in range(1, 1001):
        # 1. Seleccionar mercado y coordenadas base
        market = random.choice(MARKETS)
        # Añadir un pequeño jitter para simular dispersión de puestos
        lat_jitter = random.uniform(-0.003, 0.003)
        lon_jitter = random.uniform(-0.003, 0.003)
        lat = float(market["lat"] + lat_jitter)
        lon = float(market["lon"] + lon_jitter)

        # 2. Generar teléfono E.164 único con código lada mexicano
        if "CDMX" in market["name"]:
            area = "55"
            phone_num = 10000000 + i
        elif "Guadalajara" in market["name"]:
            area = "33"
            phone_num = 10000000 + i
        elif "Monterrey" in market["name"]:
            area = "81"
            phone_num = 10000000 + i
        else: # Colima
            area = "312"
            phone_num = 1000000 + i
        
        phone = f"+52{area}{phone_num}"

        # 3. Categoría, nombre del negocio y registro de tiempo inicial
        category = random.choice(categories)
        registration_timestamp = now_ts - random.randint(15, 60) * 86400
        
        # Generar nombre de negocio auténtico mexicano
        FIRST_NAMES = ["Juan", "María", "Pedro", "Luisa", "Carlos", "José", "Guadalupe", "Francisco", "Ana", "Miguel", "Lucía", "Antonio", "Rosa", "Jorge", "Felipe", "Manuel", "Juana", "Roberto", "Elena", "Silvia"]
        LAST_NAMES = ["Pérez", "Gómez", "Rodríguez", "Hernández", "Sánchez", "Martínez", "López", "González", "Díaz", "Flores", "Cruz", "García", "Morales", "Ramírez", "Reyes", "Ruiz", "Ortega", "Castillo", "Chávez", "Rivera"]
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        prefix = random.choice(["Don", "Doña", "Puesto de", "El Rincón de"])
        cat_es_short = {
            "seafood": random.choice(["Mariscos", "Pescadería", "Coctelería"]),
            "flowers": random.choice(["Florería", "Plantas", "Arreglos"]),
            "fruit_vegetables": random.choice(["Frutería", "Verduras", "Recaudería"]),
            "dairy": random.choice(["Cremería", "Quesos", "Lácteos"]),
            "generic": random.choice(["Novedades", "Variedades", "Mercancías"])
        }.get(category, "Comercio")
        
        if prefix in ["Don", "Doña"]:
            name = f"{cat_es_short} {prefix} {fn}"
        else:
            name = f"{prefix} {fn} {ln}"

        # 4. Generar historial de mensajes (2 a 5 interacciones)
        num_interactions = random.randint(2, 5)
        message_history: List[Dict[str, Any]] = []

        # Simular una serie de interacciones previas
        for j in range(1, num_interactions + 1):
            interaction_offset = j * random.uniform(1.5, 3.5) * 86400
            interaction_ts = registration_timestamp + interaction_offset
            if interaction_ts > now_ts:
                interaction_ts = now_ts - (num_interactions - j) * 3600

            # Consultar simulación climática estocástica
            temp = random.uniform(22.0, 36.0)
            humidity = random.uniform(0.35, 0.85)
            precip = random.uniform(0.0, 0.80)
            
            weather = WeatherState(
                temperature=temp,
                relative_humidity=humidity,
                precipitation_probability=precip
            )

            # Resolver modelos de negocio cinéticos
            shelf_life = DecayKinetics.calculate_shelf_life(category, weather)
            
            # Aproximación determinista rápida de Kelly Sizer para optimizar el tiempo de siembra
            optimal_purchase = 100.0
            if weather.precipitation_probability > 0.3:
                optimal_purchase -= 35.0 * weather.precipitation_probability
            if category == "seafood" and weather.temperature > 32.0:
                optimal_purchase *= 0.60
            elif category == "flowers" and weather.temperature > 30.0:
                optimal_purchase *= 0.70
            elif category == "dairy" and weather.temperature > 30.0:
                optimal_purchase *= 0.75
            optimal_purchase = max(10.0, min(150.0, optimal_purchase))
            pct_stock = (optimal_purchase / 100.0) * 100.0

            # Calcular el ahorro estimado en costo
            params = INVENTORY_PARAMETERS.get(category, INVENTORY_PARAMETERS["generic"])
            cost_unit = params["default_cost"]
            salvage_base = params["default_salvage"]
            decay_rate = DecayKinetics.calculate_decay_rate(category, weather)
            salvage_effective = salvage_base * float(math.exp(-decay_rate))
            avoided_units = max(0.0, 100.0 - optimal_purchase)
            saved_cost_est = float(avoided_units * (cost_unit - salvage_effective))

            # Formatear la predicción en texto
            cat_es = {
                "seafood": "Pescados y Mariscos",
                "flowers": "Flores y Plantas",
                "fruit_vegetables": "Frutas y Verduras",
                "dairy": "Lácteos y Quesos",
                "generic": "Mercancía General"
            }.get(category, "Mercancía General")
            
            tips_str = tips_by_category[category]
            
            response_text = (
                f"🔮 *Merma Cero — Oráculo Climático*\n"
                f"Categoría: {cat_es}\n\n"
                f"🌡️ *Pronóstico:* {weather.temperature:.1f}°C | Humedad: {weather.relative_humidity * 100:.0f}% | Lluvia: {weather.precipitation_probability * 100:.0f}%\n"
                f"⏳ *Vida de Anaquel Estimada:* {shelf_life:.1f} días antes de descomposición.\n\n"
                f"📦 *Recomendación de Compra:* Adquirir el *{pct_stock:.0f}%* de tu volumen diario habitual para evitar mermas.\n\n"
                f"🛠️ *Acciones de Resiliencia Climática:*\n- {tips_str}\n\n"
                f"_Protegiendo tu flujo de caja familiar._"
            )

            # Para todas menos la última interacción, o según probabilidad para la última,
            # definimos si el oráculo tuvo un acierto (True) o error (False)
            is_last = (j == num_interactions)
            if is_last:
                # La última consulta de hoy puede estar pendiente de retroalimentación
                prediction_accurate = random.choice([True, True, False, None])
            else:
                prediction_accurate = random.choice([True, True, True, False])

            query_text = random.choice(queries_by_category[category]).replace("{market}", market["name"])

            interaction_entry = {
                "timestamp": float(interaction_ts),
                "type": "inbound_request",
                "text_received": query_text,
                "weather": {
                    "temperature": float(weather.temperature),
                    "relative_humidity": float(weather.relative_humidity),
                    "precipitation_probability": float(weather.precipitation_probability)
                },
                "metrics": {
                    "shelf_life_days": float(shelf_life),
                    "optimal_purchase_pct": float(pct_stock),
                    "saved_cost_estimated": saved_cost_est
                },
                "prediction_accurate": prediction_accurate,
                "message_sent": response_text
            }
            message_history.append(interaction_entry)

        # Serializar el historial de mensajes
        history_json = json.dumps(message_history, ensure_ascii=False)

        # 5. Agregar registro a la lista de inserción masiva
        # Los campos en orden para la consulta SQL:
        # phone, latitude, longitude, inventory_category, registration_timestamp, rate_limit_tokens, rate_limit_last_update, message_history, opt_in, name, address
        data_to_insert.append((
            phone,
            lat,
            lon,
            category,
            float(registration_timestamp),
            10.0,              # rate_limit_tokens
            float(now_ts),     # rate_limit_last_update
            history_json,
            1,                 # opt_in (True para todos los pre-sembrados con interacciones)
            name,              # name
            market["name"]     # address
        ))

    # 6. Guardar registros en masa de manera transaccional y optimizada en SQLite
    start_time = time.perf_counter()
    if isinstance(repo, SQLiteVendorRepository):
        with repo.lock:
            conn = repo._get_connection()
            try:
                cursor = conn.cursor()
                # Usar una sola transacción atómica y executemany para velocidad extrema
                cursor.executemany("""
                    INSERT OR REPLACE INTO vendors (
                        phone, latitude, longitude, inventory_category, 
                        registration_timestamp, rate_limit_tokens, 
                        rate_limit_last_update, message_history, opt_in, name, address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data_to_insert)
                conn.commit()
            except Exception as e:
                conn.rollback()
                _log_seeder("ERROR", "Fallo al realizar la inserción masiva de semillas en SQLite.", {"exception": str(e)})
                raise IOError(f"Fallo en transacción masiva SQLite de siembra: {e}") from e
            finally:
                conn.close()
    else:
        # Fallback secuencial para repositorios genéricos que no sean SQLite directos (ej. en pruebas locales con JSON)
        try:
            for item in data_to_insert:
                vendor_obj = Vendor(
                    phone=item[0],
                    latitude=item[1],
                    longitude=item[2],
                    inventory_category=item[3],
                    registration_timestamp=item[4],
                    rate_limit_tokens=item[5],
                    rate_limit_last_update=item[6],
                    message_history=json.loads(item[7]),
                    opt_in=bool(item[8]),
                    name=item[9],
                    address=item[10]
                )
                repo.save(vendor_obj)
        except Exception as e:
            _log_seeder("ERROR", "Fallo al guardar semillas en repositorio de fallback.", {"exception": str(e)})
            raise e

    elapsed_time = time.perf_counter() - start_time
    _log_seeder("INFO", "Base de datos sembrada con éxito.", {"count": len(data_to_insert), "elapsed_seconds": f"{elapsed_time:.4f}"})
