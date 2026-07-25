import time
import re
import math
from typing import Tuple, Optional, List
from merma_cero.config import RATE_LIMIT_MAX_TOKENS, RATE_LIMIT_REFILL_RATE, DEFAULT_DEMAND_MEAN, DEFAULT_DEMAND_STD, INVENTORY_PARAMETERS
from merma_cero.domain.entities import Vendor, WeatherState
from merma_cero.domain.exceptions import SecurityViolationError, InvalidInputError
from merma_cero.domain.models import DecayKinetics, KellyMermaSizer
from merma_cero.application.ports import VendorRepositoryPort, WeatherPort, MessagePort, AIServicePort

class OraculoUseCase:
    """Caso de uso unificado para procesamiento conversacional asíncrono (Falkland Law)."""

    def __init__(
        self,
        repository: VendorRepositoryPort,
        weather_service: WeatherPort,
        message_sender: MessagePort,
        ai_service: AIServicePort
    ):
        self.repository = repository
        self.weather_service = weather_service
        self.message_sender = message_sender
        self.ai_service = ai_service

    def process_message(self, phone: str, text: str) -> str:
        """Procesa una solicitud entrante por WhatsApp de forma determinista y sin fricciones.
        
        Flujo de control:
            1. Recupera o registra implícitamente al vendedor.
            2. Control de opt-in de consentimiento (Meta/Twilio compliance).
            3. Procesa retroalimentación de calibración ("acierto"/"error").
            4. Aplica rate limiting (Sybil Protection).
            5. Analiza el texto para detectar actualizaciones de ubicación o categoría.
            6. Consulta el clima georreferenciado (Caché/API/Fallback).
            7. Resuelve los modelos cuánticos de decaimiento cinético y sizing.
            8. Envía y retorna la respuesta estructurada en lenguaje natural.
            9. Integra IA para recomendaciones personalizadas al giro comercial.
        """
        now = time.time()
        vendor = self.repository.get_by_phone(phone)
        text_clean = text.strip().lower()
        
        # Inferencia de parámetros desde el texto (Zero Fricción)
        category = self._parse_category(text)
        coords = self._parse_coordinates(text)

        if not vendor:
            # Registro implícito inicial (Ley de Falkland) con opt_in=False por defecto
            inferred_cat = category if category else "generic"
            lat = coords[0] if coords else 19.4326  # CDMX por defecto si no hay dato
            lon = coords[1] if coords else -99.1332
            
            is_accepting = text_clean == "acepto"
            vendor = Vendor(
                phone=phone,
                latitude=lat,
                longitude=lon,
                inventory_category=inferred_cat,
                registration_timestamp=now,
                rate_limit_tokens=float(RATE_LIMIT_MAX_TOKENS) - 1.0,
                rate_limit_last_update=now,
                opt_in=is_accepting
            )
            self.repository.save(vendor)
            
            if is_accepting:
                welcome_msg = (
                    "¡Excelente! Has activado Merma Cero. 🚀\n\n"
                    "Para poder darte recomendaciones de compra exactas y cuidar tu dinero, dime qué vendes (pescado, flores, verduras, lácteos) y tu ubicación escribiendo algo como:\n"
                    "*vendo pescado en lat 19.43 lon -99.13*"
                )
                self.message_sender.send_message(phone, welcome_msg)
                return welcome_msg
            else:
                optin_msg = (
                    "🔮 *Oráculo Merma Cero*\n\n"
                    "¡Hola! Te damos la bienvenida a Merma Cero. Diseñamos este oráculo para ayudarte a no perder dinero reduciendo tus mermas usando termodinámica e inteligencia predictiva.\n\n"
                    "Para poder enviarte pronósticos y recomendaciones de compra, necesitamos que aceptes nuestro Aviso de Privacidad y Términos de Servicio. Responde con la palabra *ACEPTO* para comenzar."
                )
                self.message_sender.send_message(phone, optin_msg)
                return optin_msg
        
        # Si el vendedor ya existe pero no ha dado opt-in
        if not vendor.opt_in:
            if text_clean == "acepto":
                vendor.opt_in = True
                self.repository.save(vendor)
                welcome_msg = (
                    "¡Excelente! Has activado Merma Cero. 🚀\n\n"
                    "Para poder darte recomendaciones de compra exactas y cuidar tu dinero, dime qué vendes (pescado, flores, verduras, lácteos) y tu ubicación escribiendo algo como:\n"
                    "*vendo pescado en lat 19.43 lon -99.13*"
                )
                self.message_sender.send_message(phone, welcome_msg)
                return welcome_msg
            else:
                optin_msg = (
                    "⚠️ Para usar el Oráculo Merma Cero y proteger tu flujo de caja familiar, por favor confirma tu consentimiento respondiendo con la palabra *ACEPTO*."
                )
                self.message_sender.send_message(phone, optin_msg)
                return optin_msg

        # Loop de calibración de retroalimentación (O8)
        if text_clean in ["acierto", "correcto", "funcionó", "error", "incorrecto", "falló"]:
            is_accurate = text_clean in ["acierto", "correcto", "funcionó"]
            
            # Buscar la última predicción en el historial
            last_pred = None
            last_pred_idx = -1
            for idx, log in enumerate(reversed(vendor.message_history)):
                if log.get("type") in ["inbound_request", "proactive_alert"] and "metrics" in log:
                    last_pred = log
                    last_pred_idx = len(vendor.message_history) - 1 - idx
                    break
            
            if last_pred:
                # Actualizar log
                last_pred["prediction_accurate"] = is_accurate
                vendor.message_history[last_pred_idx] = last_pred
                
                # Obtener ahorro estimado
                saved_cost = last_pred["metrics"].get("saved_cost_estimated", 0.0)
                self.repository.save(vendor)
                
                if is_accurate:
                    fb_msg = (
                        "¡Gracias por tu retroalimentación! 🌟 Tu reporte nos ayuda a mantener calibrado el oráculo para tu zona.\n\n"
                        f"Con la recomendación de ayer, evitaste excedentes de mercancía. Guardamos un ahorro estimado para tu negocio de *{saved_cost:.2f} pesos* en tu registro de impacto social. ¡Juntos reducimos la merma!"
                    )
                else:
                    fb_msg = (
                        "Lamentamos que la predicción de ayer no haya sido precisa. 😔\n\n"
                        "Hemos registrado este fallo en nuestro motor estocástico para recalibrar los coeficientes climáticos y el sizer Kelly en tu puesto para mañana. ¡Gracias por ayudarnos a mejorar!"
                    )
                self.message_sender.send_message(phone, fb_msg)
                return fb_msg
            else:
                no_pred_msg = "No encontré ninguna predicción reciente en tu historial para calibrar. ¡Escríbeme para solicitar tu pronóstico de hoy!"
                self.message_sender.send_message(phone, no_pred_msg)
                return no_pred_msg

        # Recargar y aplicar Rate Limiting (Token Bucket)
        elapsed = now - vendor.rate_limit_last_update
        refilled = vendor.rate_limit_tokens + elapsed * RATE_LIMIT_REFILL_RATE
        vendor.rate_limit_tokens = min(float(RATE_LIMIT_MAX_TOKENS), refilled)
        vendor.rate_limit_last_update = now

        if vendor.rate_limit_tokens < 1.0:
            raise SecurityViolationError("Cuota de consultas excedida. Intente de nuevo en una hora.")
        
        vendor.rate_limit_tokens -= 1.0

        # Actualización en caliente de parámetros si el usuario los provee
        updated = False
        if category and category != vendor.inventory_category:
            vendor.inventory_category = category
            updated = True
        if coords:
            vendor.latitude = coords[0]
            vendor.longitude = coords[1]
            updated = True
        
        self.repository.save(vendor)

        # Consultar el oráculo climático (WeatherPort maneja el colapso)
        weather = self.weather_service.get_weather(vendor.latitude, vendor.longitude)

        # Resolver el modelo físico de descomposición Arrhenius
        shelf_life = DecayKinetics.calculate_shelf_life(vendor.inventory_category, weather)
        
        # Resolver el optimizador de inventario de portafolio
        optimal_purchase = KellyMermaSizer.optimize_stock(
            category=vendor.inventory_category,
            weather=weather,
            base_demand_mean=DEFAULT_DEMAND_MEAN,
            base_demand_std=DEFAULT_DEMAND_STD
        )

        # Calcular el ahorro estimado en costo si la compra es menor a la habitual
        params = INVENTORY_PARAMETERS.get(vendor.inventory_category, INVENTORY_PARAMETERS["generic"])
        cost_unit = params["default_cost"]
        salvage_base = params["default_salvage"]
        decay_rate = DecayKinetics.calculate_decay_rate(vendor.inventory_category, weather)
        salvage_effective = salvage_base * float(math.exp(-decay_rate))
        
        avoided_units = max(0.0, DEFAULT_DEMAND_MEAN - optimal_purchase)
        saved_cost_est = avoided_units * (cost_unit - salvage_effective)

        # Formatear la respuesta optimizada
        response_text = self._format_response(vendor, weather, shelf_life, optimal_purchase)
        
        # Guardar en la bitácora del vendedor y persistir en base de datos
        pct_stock = (optimal_purchase / DEFAULT_DEMAND_MEAN) * 100.0
        log_entry = {
            "timestamp": now,
            "type": "inbound_request",
            "text_received": text,
            "weather": {
                "temperature": weather.temperature,
                "relative_humidity": weather.relative_humidity,
                "precipitation_probability": weather.precipitation_probability
            },
            "metrics": {
                "shelf_life_days": shelf_life,
                "optimal_purchase_pct": pct_stock,
                "saved_cost_estimated": saved_cost_est
            },
            "prediction_accurate": None,  # Pendiente de retroalimentación
            "message_sent": response_text
        }
        vendor.message_history.append(log_entry)
        self.repository.save(vendor)

        # Envío asíncrono
        self.message_sender.send_message(phone, response_text)
        
        return response_text

    def _parse_category(self, text: str) -> Optional[str]:
        """Deduce la categoría del producto del vendedor usando NLP regex ligero."""
        text_lower = text.lower()
        mapping = {
            "seafood": ["pescado", "marisco", "camaron", "ostion", "pulpo", "jaiba", "seafood"],
            "flowers": ["flor", "flores", "rosas", "arreglo", "ramo", "clavel", "flowers"],
            "fruit_vegetables": ["verdura", "fruta", "limon", "aguacate", "jitomate", "manzana", "platano", "fruit", "vegetables"],
            "dairy": ["leche", "queso", "crema", "yogur", "lacteo", "dairy"],
        }
        for category, keywords in mapping.items():
            for kw in keywords:
                if kw in text_lower:
                    return category
        return None

    def _parse_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Busca patrones de coordenadas decimales (latitud, longitud) en el texto."""
        # Detecta formatos tipo "19.43, -99.13" o "lat 19.43 lon -99.13"
        pattern = r"(-?\d+\.\d+)(?:\s*,\s*|\s+(?:lon\s+)?)(-?\d+\.\d+)"
        match = re.search(pattern, text)
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    return lat, lon
            except ValueError:
                pass
        return None

    def _format_response(
        self,
        vendor: Vendor,
        weather: WeatherState,
        shelf_life: float,
        optimal_purchase: float
    ) -> str:
        """Genera el mensaje final adaptado a la economía informal (ESG/Fricción Cero)."""
        cat_es = {
            "seafood": "Pescados y Mariscos",
            "flowers": "Flores y Plantas",
            "fruit_vegetables": "Frutas y Verduras",
            "dairy": "Lácteos y Quesos",
            "generic": "Mercancía General"
        }.get(vendor.inventory_category, "Mercancía General")

        # Conversión a porcentaje del stock recomendado sobre la demanda habitual (100 unidades)
        pct_stock = (optimal_purchase / DEFAULT_DEMAND_MEAN) * 100.0

        # Obtener recomendaciones personalizadas con IA o fallback de reglas
        tips_str = self.ai_service.get_recommendation(
            category=vendor.inventory_category,
            weather=weather,
            shelf_life=shelf_life,
            optimal_purchase_pct=pct_stock
        )

        # Construcción de mensaje compacto
        return (
            f"🔮 *Merma Cero — Oráculo Climático*\n"
            f"Categoría: {cat_es}\n\n"
            f"🌡️ *Pronóstico:* {weather.temperature:.1f}°C | Humedad: {weather.relative_humidity * 100:.0f}% | Lluvia: {weather.precipitation_probability * 100:.0f}%\n"
            f"⏳ *Vida de Anaquel Estimada:* {shelf_life:.1f} días antes de descomposición.\n\n"
            f"📦 *Recomendación de Compra:* Adquirir el *{pct_stock:.0f}%* de tu volumen diario habitual para evitar mermas.\n\n"
            f"🛠️ *Acciones de Resiliencia Climática:*\n{tips_str}\n\n"
            f"_Protegiendo tu flujo de caja familiar._"
        )

    def check_and_send_alerts(self) -> List[str]:
        """Escanea todos los vendedores y proactivamente les envía alertas si detecta riesgo climático."""
        vendors = self.repository.get_all()
        sent_alerts = []

        for vendor in vendors:
            # Consultar clima para el vendedor
            weather = self.weather_service.get_weather(vendor.latitude, vendor.longitude)
            
            # Condición de alerta: temperatura extrema o lluvia sustancial
            has_alert = weather.temperature > 30.0 or weather.precipitation_probability > 0.4
            
            if has_alert:
                # Calcular vida de anaquel y stock óptimo
                shelf_life = DecayKinetics.calculate_shelf_life(vendor.inventory_category, weather)
                optimal_purchase = KellyMermaSizer.optimize_stock(
                    category=vendor.inventory_category,
                    weather=weather,
                    base_demand_mean=DEFAULT_DEMAND_MEAN,
                    base_demand_std=DEFAULT_DEMAND_STD
                )
                pct_stock = (optimal_purchase / DEFAULT_DEMAND_MEAN) * 100.0
                
                # Calcular el ahorro estimado en costo
                params = INVENTORY_PARAMETERS.get(vendor.inventory_category, INVENTORY_PARAMETERS["generic"])
                cost_unit = params["default_cost"]
                salvage_base = params["default_salvage"]
                decay_rate = DecayKinetics.calculate_decay_rate(vendor.inventory_category, weather)
                salvage_effective = salvage_base * float(math.exp(-decay_rate))
                
                avoided_units = max(0.0, DEFAULT_DEMAND_MEAN - optimal_purchase)
                saved_cost_est = avoided_units * (cost_unit - salvage_effective)

                # Obtener recomendación adaptada vía IA o fallback
                recommendation = self.ai_service.get_recommendation(
                    category=vendor.inventory_category,
                    weather=weather,
                    shelf_life=shelf_life,
                    optimal_purchase_pct=pct_stock
                )
                
                cat_es = {
                    "seafood": "Pescados y Mariscos",
                    "flowers": "Flores y Plantas",
                    "fruit_vegetables": "Frutas y Verduras",
                    "dairy": "Lácteos y Quesos",
                    "generic": "Mercancía General"
                }.get(vendor.inventory_category, "Mercancía General")
                
                alert_message = (
                    f"🚨 *ALERTA CLIMÁTICA CRÍTICA — Merma Cero*\n"
                    f"Giro: {cat_es}\n\n"
                    f"Detectamos condiciones de riesgo en tu zona de trabajo:\n"
                    f"🌡️ Temperatura: {weather.temperature:.1f}°C | 🌧️ Probabilidad de Lluvia: {weather.precipitation_probability * 100:.0f}%\n\n"
                    f"⏳ *Vida de Anaquel Estimada:* {shelf_life:.1f} días antes de descomposición.\n"
                    f"📦 *Sugerencia de Inventario:* Adquirir el *{pct_stock:.0f}%* de tu stock habitual para mitigar pérdidas.\n\n"
                    f"💡 *Recomendación de la IA:*\n{recommendation}\n\n"
                    f"_Protegiendo tu flujo de caja familiar._"
                )
                
                self.message_sender.send_message(vendor.phone, alert_message)
                
                # Registrar alerta en el historial del vendedor
                log_entry = {
                    "timestamp": time.time(),
                    "type": "proactive_alert",
                    "weather": {
                        "temperature": weather.temperature,
                        "relative_humidity": weather.relative_humidity,
                        "precipitation_probability": weather.precipitation_probability
                    },
                    "metrics": {
                        "shelf_life_days": shelf_life,
                        "optimal_purchase_pct": pct_stock,
                        "saved_cost_estimated": saved_cost_est
                    },
                    "prediction_accurate": None,  # Pendiente de retroalimentación
                    "message_sent": alert_message
                }
                vendor.message_history.append(log_entry)
                self.repository.save(vendor)
                
                sent_alerts.append(vendor.phone)
                
        return sent_alerts

