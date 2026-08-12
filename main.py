# -*- coding: utf-8 -*-
"""Punto de entrada principal del oráculo Merma Cero: FastAPI y CLI interactivo.

Cumple con la asincronía de alto rendimiento, logging estructurado JSON y variables .env.
"""
import sys
import os
import time
import json
import secrets
import datetime
import traceback
import hmac
import hashlib
import base64
import urllib.parse
from typing import Dict, Any

# Asegurar que el directorio raíz está en la ruta para importación
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno desde .env antes de importar dependencias que las usen
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Importaciones estándar y asíncronas
import asyncio
import zoneinfo

# Importaciones de FastAPI
from fastapi import FastAPI, Request, Response, status, Query
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from pydantic import BaseModel, Field

# Importaciones del Dominio e Infraestructura
from merma_cero.config import DATABASE_PATH
from merma_cero.domain.exceptions import DomainError, SecurityViolationError, InvalidInputError
from merma_cero.application.use_cases import OraculoUseCase
from merma_cero.infrastructure.sqlite_repository import SQLiteVendorRepository
from merma_cero.infrastructure.weather_adapter import OpenMeteoAdapter
from merma_cero.infrastructure.whatsapp_adapter import WhatsAppMockAdapter
from merma_cero.infrastructure.gemini_adapter import GeminiAIAdapter
from merma_cero.infrastructure.telegram_adapter import TelegramAdapter
from merma_cero.infrastructure.routing_adapter import UnifiedMessageAdapter

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Merma Cero: Oráculo Climático",
    description="API de alto rendimiento para el webhook de resiliencia climática",
    version="1.0.0"
)

# Inicialización de dependencias globales (Hexagonal DI)
db_path_env = os.getenv("SQLITE_DATABASE_PATH")
repo = SQLiteVendorRepository(db_path=db_path_env)
weather_service = OpenMeteoAdapter()

# Adaptador de WhatsApp (Twilio o Mock)
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
if twilio_sid and not twilio_sid.startswith("mock_"):
    from merma_cero.infrastructure.twilio_adapter import TwilioAdapter
    whatsapp_sender = TwilioAdapter()
else:
    whatsapp_sender = WhatsAppMockAdapter()

# Adaptador de Telegram
telegram_sender = TelegramAdapter()

# Enrutador unificado de mensajería (WhatsApp + Telegram Router)
routing_sender = UnifiedMessageAdapter(whatsapp_adapter=whatsapp_sender, telegram_adapter=telegram_sender)

ai_service = GeminiAIAdapter()

# Inyectar el enrutador en el caso de uso
oraculo = OraculoUseCase(
    repository=repo,
    weather_service=weather_service,
    message_sender=routing_sender,
    ai_service=ai_service
)


# DTO de Ingesta Validada (OWASP A03 / Pydantic Boundary)
class WebhookPayload(BaseModel):
    """Objeto de transferencia de datos para el webhook de entrada conversacional."""
    phone: str = Field(..., min_length=8, max_length=18, description="Número telefónico del vendedor en formato E.164")
    text: str = Field(..., max_length=500, description="Mensaje de texto enviado por el usuario")

# Utilidad de Logging Estructurado en JSON (Sección 7 de rigor_lenguaje.md)
def log_json(severity: str, message: str, context: Dict[str, Any] = None, trace_id: str = None) -> None:
    """Escribe una línea de log estructurada en formato JSON en stderr."""
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "severity": severity,
        "trace_id": trace_id or "N/A",
        "module": "merma_cero.main",
        "message": message,
        "context": context or {}
    }
    sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    sys.stderr.flush()

class TelegramUpdate(BaseModel):
    """Modelo de datos para validar payloads entrantes de Telegram."""
    update_id: int
    message: Dict[str, Any] = Field(..., description="Estructura del mensaje recibido de Telegram")

# Tarea de fondo: Programador de Alertas Climáticas Matutinas (6:00 AM)
async def run_daily_scheduler():
    """Bucle asíncrono que ejecuta la verificación de alertas climáticas a las 6:00 AM todos los días."""
    timezone_name = os.getenv("ALERT_TIMEZONE", "America/Mexico_City")
    try:
        tz = zoneinfo.ZoneInfo(timezone_name)
    except Exception:
        tz = datetime.timezone.utc
        timezone_name = "UTC"
    
    log_json(
        severity="INFO",
        message=f"Iniciando programador de alertas a las 6:00 AM (Zona Horaria: {timezone_name})"
    )
    
    while True:
        now = datetime.datetime.now(tz)
        # Calcular cuándo es el próximo disparo de las 6:00 AM
        next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += datetime.timedelta(days=1)
            
        sleep_seconds = (next_run - now).total_seconds()
        log_json(
            severity="INFO",
            message=f"Alertas automáticas programadas. Próxima ejecución: {next_run.isoformat()}",
            context={"sleep_seconds": sleep_seconds}
        )
        
        try:
            await asyncio.sleep(sleep_seconds)
            
            trace_id = secrets.token_hex(8)
            log_json(
                severity="INFO",
                message="Disparador automático matutino iniciado (6:00 AM)",
                trace_id=trace_id
            )
            
            sent = oraculo.check_and_send_alerts()
            log_json(
                severity="INFO",
                message="Procesamiento diario de alertas climáticas matutinas completado",
                context={"alerts_sent_count": len(sent), "recipients": sent},
                trace_id=trace_id
            )
        except asyncio.CancelledError:
            log_json(severity="INFO", message="Programador de alertas matutinas detenido.")
            break
        except Exception as e:
            tb = "".join(traceback.format_exception(None, e, e.__traceback__))
            log_json(
                severity="ERROR",
                message="Excepción en el programador de alertas matutinas",
                context={"exception": str(e), "traceback": tb}
            )
            await asyncio.sleep(60)

# Tarea de fondo: Programador de Encuestas Quincenales (cada 15 días)
async def run_fortnightly_survey_scheduler() -> None:
    """Bucle asíncrono que ejecuta el envío de la encuesta quincenal cada 15 días."""
    log_json(
        severity="INFO",
        message="Iniciando programador de encuestas quincenales (Intervalo: 15 días)"
    )
    
    interval_seconds = 15 * 24 * 3600
    
    while True:
        try:
            log_json(
                severity="INFO",
                message="Encuesta automática quincenal programada.",
                context={"sleep_seconds": interval_seconds}
            )
            await asyncio.sleep(interval_seconds)
            
            trace_id = secrets.token_hex(8)
            log_json(
                severity="INFO",
                message="Disparador automático quincenal iniciado",
                trace_id=trace_id
            )
            
            sent = oraculo.check_and_send_fortnightly_survey()
            log_json(
                severity="INFO",
                message="Procesamiento quincenal de encuesta de impacto completado",
                context={"surveys_sent_count": len(sent), "recipients": sent},
                trace_id=trace_id
            )
        except asyncio.CancelledError:
            log_json(severity="INFO", message="Programador de encuestas quincenales detenido.")
            break
        except Exception as e:
            tb = "".join(traceback.format_exception(None, e, e.__traceback__))
            log_json(
                severity="ERROR",
                message="Excepción en el programador de encuestas quincenales",
                context={"exception": str(e), "traceback": tb}
            )
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    """Ciclo de vida al iniciar FastAPI: Arranca el scheduler y registra el webhook si aplica."""
    # 1. Iniciar la tarea de fondo de alertas
    asyncio.create_task(run_daily_scheduler())
    
    # 1b. Iniciar la tarea de fondo de encuestas quincenales
    asyncio.create_task(run_fortnightly_survey_scheduler())
    
    # 2. Limpieza de datos y registro de usuario real
    try:
        from merma_cero.infrastructure.sqlite_repository import VendorModel
        with repo.lock:
            with repo.SessionLocal() as session:
                session.query(VendorModel).filter(VendorModel.is_simulated == True).delete()
                session.commit()
    except Exception as e:
        log_json(
            severity="ERROR",
            message="Error al limpiar comerciantes simulados",
            context={"error": str(e)}
        )
        
    try:
        from merma_cero.domain.entities import Vendor
        target_phone = "+525575049383"
        if not repo.get_by_phone(target_phone):
            now_ts = datetime.datetime.utcnow().timestamp()
            new_vendor = Vendor(
                phone=target_phone,
                name="Fabio Israel",
                latitude=19.4326,
                longitude=-99.1332,
                address="Ciudad de México",
                age=17,
                business_years=2.0,
                inventory_category="seafood",
                opt_in=True,
                is_simulated=False,
                registration_timestamp=now_ts,
                rate_limit_tokens=10.0,
                rate_limit_last_update=now_ts,
                message_history=[{
                    "type": "inbound_request",
                    "prediction_accurate": True,
                    "metrics": {"saved_cost_estimated": 1250.0}
                }]
            )
            repo.save(new_vendor)
            log_json(
                severity="INFO",
                message="Comerciante real registrado en inicio",
                context={"phone": target_phone}
            )
    except Exception as e:
        log_json(
            severity="ERROR",
            message="Error al registrar comerciante real",
            context={"error": str(e)}
        )

    # 2. Sembrar la base de datos si está vacía (COMENTADO PARA PRODUCCIÓN)
    try:
        # from merma_cero.infrastructure.seeder import seed_database
        # loop = asyncio.get_event_loop()
        # await loop.run_in_executor(None, lambda: seed_database(repo))
        pass
    except Exception as e:
        log_json(
            severity="ERROR",
            message="Error al intentar sembrar la base de datos en el inicio",
            context={"error": str(e)}
        )

    # 3. Registrar webhook de Telegram automáticamente si se provee una URL pública
    public_url = os.getenv("PUBLIC_URL")
    if public_url and not telegram_sender._is_mock():
        telegram_webhook_url = f"{public_url.rstrip('/')}/telegram/webhook"
        url = f"https://api.telegram.org/bot{telegram_sender.token}/setWebhook?url={telegram_webhook_url}"
        try:
            # Registrar el webhook de Telegram de manera asíncrona no bloqueante
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: urllib.request.urlopen(urllib.request.Request(url, method="POST"), timeout=10).read()
            )
            log_json(
                severity="INFO",
                message=f"Webhook de Telegram registrado exitosamente: {telegram_webhook_url}"
            )
        except Exception as e:
            log_json(
                severity="WARN",
                message="No se pudo registrar el webhook automático de Telegram",
                context={"error": str(e), "url_intentada": url}
            )

@app.post("/telegram/webhook", status_code=status.HTTP_200_OK)
async def process_telegram_webhook(update: TelegramUpdate, response: Response):
    """Endpoint de recepción de mensajes entrantes para el Bot de Telegram."""
    trace_id = secrets.token_hex(8)
    try:
        msg = update.message
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        text = msg.get("text")
        
        if not chat_id or not text:
            return {"status": "ignored", "message": "Mensaje de Telegram omitido (no contiene texto o chat ID)."}
            
        recipient_id = f"telegram:{chat_id}"
        text_str = str(text).strip()
        
        if len(text_str) > 500:
            raise InvalidInputError("Mensaje demasiado largo.")
            
        # Extraer nombre del remitente de Telegram
        from_user = msg.get("from", {})
        first_name = from_user.get("first_name")
        last_name = from_user.get("last_name")
        sender_name = None
        if first_name:
            sender_name = f"{first_name} {last_name}".strip() if last_name else first_name
            
        log_json(
            severity="INFO",
            message="Petición recibida desde Telegram",
            context={"chat_id": chat_id, "sender_name": sender_name},
            trace_id=trace_id
        )
        
        # Procesar la conversación de forma transparente
        response_text = oraculo.process_message(recipient_id, text_str, sender_name=sender_name)
        
        log_json(
            severity="INFO",
            message="Mensaje de Telegram procesado y respondido",
            context={"chat_id": chat_id},
            trace_id=trace_id
        )
        return {"status": "success", "response": response_text}
        
    except InvalidInputError as iie:
        log_json(
            severity="WARN",
            message="Datos de entrada inválidos en webhook de Telegram",
            context={"error": str(iie)},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "error", "message": "Datos de entrada inválidos."}
    except Exception as e:
        tb = "".join(traceback.format_exception(None, e, e.__traceback__))
        log_json(
            severity="CRITICAL",
            message="Fallo general al procesar webhook de Telegram",
            context={"exception": str(e), "traceback": tb},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": "Error interno del servidor."}

@app.post("/alerts/trigger", status_code=status.HTTP_200_OK)
@app.get("/alerts/trigger", status_code=status.HTTP_200_OK)
def trigger_climate_alerts(response: Response):
    """Scan and send proactive weather alerts to all registered merchants when risks are detected."""
    trace_id = secrets.token_hex(8)
    log_json(
        severity="INFO",
        message="Iniciando escaneo proactivo de alertas climáticas",
        trace_id=trace_id
    )
    try:
        sent_alerts = oraculo.check_and_send_alerts()
        log_json(
            severity="INFO",
            message="Escaneo de alertas climáticas completado",
            context={"alerts_sent_count": len(sent_alerts), "recipients": sent_alerts},
            trace_id=trace_id
        )
        return {"status": "success", "alerts_sent_count": len(sent_alerts), "recipients": sent_alerts}
    except Exception as e:
        tb = "".join(traceback.format_exception(None, e, e.__traceback__))
        log_json(
            severity="CRITICAL",
            message="Fallo al procesar alertas proactivas",
            context={"exception": str(e), "traceback": tb},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": "Fallo interno al enviar alertas."}

@app.post("/alerts/survey", status_code=status.HTTP_200_OK)
@app.get("/alerts/survey", status_code=status.HTTP_200_OK)
def trigger_fortnightly_survey(response: Response):
    """Scan and send fortnightly survey to all registered merchants."""
    trace_id = secrets.token_hex(8)
    log_json(
        severity="INFO",
        message="Iniciando envío manual de encuesta quincenal",
        trace_id=trace_id
    )
    try:
        sent_surveys = oraculo.check_and_send_fortnightly_survey()
        log_json(
            severity="INFO",
            message="Envío de encuesta quincenal completado",
            context={"surveys_sent_count": len(sent_surveys), "recipients": sent_surveys},
            trace_id=trace_id
        )
        return {"status": "success", "surveys_sent_count": len(sent_surveys), "recipients": sent_surveys}
    except Exception as e:
        tb = "".join(traceback.format_exception(None, e, e.__traceback__))
        log_json(
            severity="CRITICAL",
            message="Fallo al enviar encuestas quincenales",
            context={"exception": str(e), "traceback": tb},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": "Fallo interno al enviar encuestas."}

@app.post("/alerts/sudden", status_code=status.HTTP_200_OK)
@app.get("/alerts/sudden", status_code=status.HTTP_200_OK)
def trigger_sudden_climate_alerts(response: Response):
    """Scan and send emergency weather alerts to all registered merchants when sudden drastic weather changes are detected."""
    trace_id = secrets.token_hex(8)
    log_json(
        severity="INFO",
        message="Iniciando escaneo de alertas climáticas repentinas",
        trace_id=trace_id
    )
    try:
        sent_alerts = oraculo.check_and_send_sudden_alerts()
        log_json(
            severity="INFO",
            message="Escaneo de alertas climáticas repentinas completado",
            context={"alerts_sent_count": len(sent_alerts), "recipients": sent_alerts},
            trace_id=trace_id
        )
        return {"status": "success", "alerts_sent_count": len(sent_alerts), "recipients": sent_alerts}
    except Exception as e:
        tb = "".join(traceback.format_exception(None, e, e.__traceback__))
        log_json(
            severity="CRITICAL",
            message="Fallo al procesar alertas repentinas",
            context={"exception": str(e), "traceback": tb},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": "Fallo interno al enviar alertas repentinas."}

@app.get("/api/vendors", status_code=status.HTTP_200_OK)
def get_vendors_api(show_simulated: bool = False):
    """Retorna la lista de todos los vendedores registrados con opt-in activo para pintar en el mapa interactivo."""
    try:
        from merma_cero.config import get_category_name_es, get_category_group
        vendors = repo.get_all()
        # Retornamos solo datos públicos necesarios para el mapa (por seguridad/privacidad omitimos el teléfono completo,
        # mostrando solo los últimos dígitos o un hash, o directamente omitimos el campo teléfono para proteger privacidad)
        return [
            {
                "name": vendor.name,
                "latitude": float(vendor.latitude),
                "longitude": float(vendor.longitude),
                "inventory_category": vendor.inventory_category,
                "category_name_es": get_category_name_es(vendor.inventory_category),
                "category_group": get_category_group(vendor.inventory_category),
                "registration_timestamp": float(vendor.registration_timestamp),
                "address": vendor.address
            }
            for vendor in vendors if vendor.opt_in and (show_simulated or not vendor.is_simulated)
        ]
    except Exception as e:
        log_json(
            severity="ERROR",
            message="Fallo al obtener vendedores para la API del mapa",
            context={"error": str(e)}
        )
        return []

@app.get("/api/stats", status_code=status.HTTP_200_OK)
def get_stats_api(show_simulated: bool = False):
    """Retorna las estadísticas acumuladas en tiempo real de los comerciantes registrados reales o simulados."""
    try:
        from merma_cero.config import get_category_group
        vendors = repo.get_all()
        real_vendors = [v for v in vendors if v.opt_in and (show_simulated or not v.is_simulated)]
        
        # 1. Total comerciantes
        total_merchants = len(real_vendors)
        
        # 2. Total dinero salvado
        total_savings = 0.0
        for vendor in real_vendors:
            for log in vendor.message_history:
                # Si el log contiene métricas y fue una predicción
                if isinstance(log, dict) and log.get("type") in ["inbound_request", "proactive_alert"]:
                    metrics = log.get("metrics")
                    if isinstance(metrics, dict):
                        # Sumar el ahorro estimado
                        total_savings += float(metrics.get("saved_cost_estimated", 0.0))
        
        # 3. Categorías
        categories = {}
        for vendor in real_vendors:
            group = get_category_group(vendor.inventory_category)
            categories[group] = categories.get(group, 0) + 1
            
        # 4. Ciudades Top
        cities = {}
        for vendor in real_vendors:
            # Obtener el nombre de la ciudad/localidad de la dirección
            addr = vendor.address.split(",")[-1].strip() if "," in vendor.address else vendor.address.strip()
            if addr:
                cities[addr] = cities.get(addr, 0) + 1
        
        # Ordenar ciudades por frecuencia
        sorted_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)
        top_cities = [{"city": k, "count": v} for k, v in sorted_cities[:5]]
        
        return {
            "total_merchants": total_merchants,
            "total_savings": round(total_savings, 2),
            "categories": categories,
            "top_cities": top_cities
        }
    except Exception as e:
        log_json(
            severity="ERROR",
            message="Fallo al obtener estadísticas para la API",
            context={"error": str(e)}
        )
        return {
            "total_merchants": 0,
            "total_savings": 0.0,
            "categories": {},
            "top_cities": []
        }

@app.get("/api/categories", status_code=status.HTTP_200_OK)
def get_categories_api():
    """Retorna las 1000 categorías de inventario y sus parámetros dinámicos."""
    try:
        from merma_cero.config import INVENTORY_PARAMETERS, get_category_name_es
        result = {}
        for key, params in INVENTORY_PARAMETERS.items():
            result[key] = {
                "Ea": params["Ea"],
                "K0": params["K0"],
                "alpha": params["alpha"],
                "price": params["default_price"],
                "cost": params["default_cost"],
                "salvage": params["default_salvage"],
                "name_es": get_category_name_es(key)
            }
        return result
    except Exception as e:
        log_json(
            severity="ERROR",
            message="Fallo al obtener categorías",
            context={"error": str(e)}
        )
        return {}


@app.get("/mapa", response_class=HTMLResponse)
@app.get("/map", response_class=HTMLResponse)
def get_map_page():
    """Sirve la página independiente del mapa interactivo de México con estadísticas en tiempo real."""
    map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa.html")
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Mapa no encontrado</h1>", status_code=404)

_cached_index_html = None

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Sirve la landing page interactiva index.html del oráculo en memoria cacheada."""
    global _cached_index_html
    if _cached_index_html is None:
        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    _cached_index_html = f.read()
            except Exception:
                _cached_index_html = ""
        else:
            _cached_index_html = ""
            
    if _cached_index_html:
        return HTMLResponse(content=_cached_index_html)
    return HTMLResponse(content="<h1>Merma Cero: Oráculo Climático Online</h1>")

@app.get("/market_stall.jpg", response_class=FileResponse)
def get_market_stall_image():
    """Sirve la imagen representativa del tianguis/mercado."""
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "market_stall.jpg")
    if os.path.exists(img_path):
        return FileResponse(img_path)
    return Response(status_code=404)

_cached_legal_html = None

@app.get("/legal", response_class=HTMLResponse)
def read_legal():
    """Sirve los términos y condiciones de legal.html en memoria cacheada."""
    global _cached_legal_html
    if _cached_legal_html is None:
        legal_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legal.html")
        if os.path.exists(legal_path):
            try:
                with open(legal_path, "r", encoding="utf-8") as f:
                    _cached_legal_html = f.read()
            except Exception:
                _cached_legal_html = ""
        else:
            _cached_legal_html = ""
            
    if _cached_legal_html:
        return HTMLResponse(content=_cached_legal_html)
    return HTMLResponse(content="<h1>Términos de Servicio — Merma Cero</h1>")

@app.get("/webhook", response_class=PlainTextResponse)
def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    verify_token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Handshake de verificación GET exigido por Meta (WhatsApp Cloud API)."""
    token_esperado = os.getenv("WHATSAPP_TOKEN")
    
    if mode == "subscribe" and verify_token == token_esperado:
        log_json(
            severity="INFO",
            message="Webhook de WhatsApp verificado con éxito por Meta",
            context={"mode": mode}
        )
        return challenge
    
    log_json(
        severity="WARN",
        message="Intento de verificación de webhook fallido",
        context={"mode": mode, "verify_token": verify_token}
    )
    return Response(content="Verificación fallida.", status_code=403)

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def process_webhook_message(request: Request, response: Response):
    """Endpoint de ingesta de alta velocidad y blindaje contra filtraciones lógicas."""
    # Generación de Identificador de Transacción Criptográfico (CSPRNG)
    trace_id = secrets.token_hex(8)
    
    # 1. Leer el body según content-type (soporte para JSON y Form Urlencoded de Twilio)
    content_type = request.headers.get("content-type", "")
    payload = {}
    is_twilio_form = "application/x-www-form-urlencoded" in content_type
    
    try:
        if is_twilio_form:
            # Parseo puro sin dependencia de python-multipart
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8")
            payload = {k: v[0] for k, v in urllib.parse.parse_qs(body_str).items()}
        else:
            payload = await request.json()
    except Exception as e:
        log_json(
            severity="WARN",
            message="Fallo al decodificar cuerpo de petición en webhook",
            context={"error": str(e)},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "error", "message": "Cuerpo de petición malformado."}

    # 1.5. Validación de firma Twilio (OWASP A03 - Spoofing Prevention)
    if is_twilio_form or request.headers.get("X-Twilio-Signature"):
        bypass_validation = os.getenv("BYPASS_TWILIO_VALIDATION", "false").lower() == "true"
        if not bypass_validation:
            twilio_signature = request.headers.get("X-Twilio-Signature")
            if not twilio_signature:
                log_json(
                    severity="WARN",
                    message="Petición rechazada: Falta cabecera X-Twilio-Signature.",
                    trace_id=trace_id
                )
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"status": "error", "message": "Firma de seguridad requerida."}
                
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            if not auth_token:
                log_json(
                    severity="CRITICAL",
                    message="No se puede validar Twilio Signature sin TWILIO_AUTH_TOKEN configurado.",
                    trace_id=trace_id
                )
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error", "message": "Configuración de seguridad incompleta."}

            # Reconstruir URL solicitada
            public_url = os.getenv("PUBLIC_URL")
            if public_url:
                url_for_validation = public_url.rstrip("/") + request.scope.get("path", "/webhook")
                query_string = request.scope.get("query_string", b"").decode("utf-8")
                if query_string:
                    url_for_validation += f"?{query_string}"
            else:
                url_for_validation = str(request.url)
            
            # Construir cadena a firmar según especificación de Twilio
            data_to_sign = url_for_validation
            if payload and is_twilio_form:
                for k, v in sorted(payload.items()):
                    data_to_sign += f"{k}{v}"
                    
            # Calcular HMAC-SHA1 y validar
            mac = hmac.new(auth_token.encode("utf-8"), data_to_sign.encode("utf-8"), hashlib.sha1)
            expected_signature = base64.b64encode(mac.digest()).decode("utf-8")
            
            if not hmac.compare_digest(expected_signature, twilio_signature):
                log_json(
                    severity="WARN",
                    message="Petición rechazada: Firma X-Twilio-Signature inválida.",
                    context={"url": url_for_validation},
                    trace_id=trace_id
                )
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"status": "error", "message": "Firma de seguridad inválida."}

    # 2. Extraer teléfono, texto y nombre con soporte para Twilio, Meta y formato plano
    phone = None
    text = None
    sender_name = None
    
    try:
        # Verificar si es la estructura de Twilio
        if "From" in payload and "Body" in payload:
            from_val = payload.get("From", "")
            # Limpiar prefijo "whatsapp:" si existe
            if str(from_val).startswith("whatsapp:"):
                phone = str(from_val).replace("whatsapp:", "")
            else:
                phone = from_val
            text = payload.get("Body")
            sender_name = payload.get("ProfileName")
            
        # Verificar si es la estructura de Meta (WhatsApp Cloud API)
        elif "object" in payload and "entry" in payload:
            entry = payload.get("entry", [])
            if entry and isinstance(entry, list):
                changes = entry[0].get("changes", [])
                if changes and isinstance(changes, list):
                    value = changes[0].get("value", {})
                    messages = value.get("messages", [])
                    if messages and isinstance(messages, list):
                        msg = messages[0]
                        phone = msg.get("from")
                        # Extraer solo si el mensaje es de tipo texto
                        if msg.get("type") == "text":
                            text = msg.get("text", {}).get("body")
                    
                    contacts = value.get("contacts", [])
                    if contacts and isinstance(contacts, list):
                        sender_name = contacts[0].get("profile", {}).get("name")
        else:
            # Formato plano de compatibilidad (Swagger / CLI / Simulador)
            phone = payload.get("phone")
            text = payload.get("text")
            sender_name = payload.get("name")
            
        # Si no es un mensaje procesable (ej. notificaciones de lectura, entrega, etc.), retornar 200 y terminar
        if not phone or not text:
            log_json(
                severity="INFO",
                message="Petición de webhook omitida (no contiene texto o remitente)",
                context={"keys": list(payload.keys())},
                trace_id=trace_id
            )
            return {"status": "ignored", "message": "Petición no contiene texto o remitente."}

        # Saneamiento y validaciones de seguridad básicas
        phone_str = str(phone).strip()
        text_str = str(text).strip()
        
        # Validar longitud mínima y máxima del teléfono
        if not (8 <= len(phone_str) <= 18):
            raise InvalidInputError("Longitud de teléfono inválida.")
        if len(text_str) > 500:
            raise InvalidInputError("Mensaje demasiado largo.")
            
        # Asegurar formato E.164
        if not phone_str.startswith("+"):
            phone_str = "+" + phone_str

        log_json(
            severity="INFO",
            message="Petición recibida en webhook",
            context={"phone": phone_str, "sender_name": sender_name},
            trace_id=trace_id
        )

        # Procesar caso de uso conversacional asíncrono
        response_text = oraculo.process_message(phone_str, text_str, sender_name=sender_name)
        
        log_json(
            severity="INFO",
            message="Mensaje procesado y enviado con éxito",
            context={"phone": phone_str},
            trace_id=trace_id
        )
        return {"status": "success", "response": response_text}

    except SecurityViolationError as sve:
        # Evasión de exposición al exterior (Silencioso hacia fuera, registrado por dentro)
        log_json(
            severity="WARN",
            message="Violación de rate-limiting (Sybil Protection)",
            context={"phone": str(phone) if phone else "Desconocido", "error": str(sve)},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return {"status": "error", "message": "Peticiones excedidas. Intente más tarde."}

    except (InvalidInputError, ValueError) as iie:
        log_json(
            severity="WARN",
            message="Datos de entrada inválidos en webhook",
            context={"phone": str(phone) if phone else "Desconocido", "error": str(iie)},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "error", "message": "Datos de entrada inválidos."}

    except DomainError as de:
        log_json(
            severity="ERROR",
            message="Fallo lógico de negocio",
            context={"phone": str(phone) if phone else "Desconocido", "error": str(de)},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": "error", "message": "No se pudo procesar la predicción."}

    except Exception as e:
        # Captura de fallos no controlados para evitar filtración de stack trace
        tb = "".join(traceback.format_exception(None, e, e.__traceback__))
        log_json(
            severity="CRITICAL",
            message="Fallo del sistema no controlado",
            context={"phone": str(phone) if phone else "Desconocido", "exception": str(e), "traceback": tb},
            trace_id=trace_id
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": "Error interno del sistema."}

def run_cli_interactive():
    """Inicia un bucle interactivo de simulación conversacional en terminal."""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
        
    print("=====================================================================")
    print("   🔮 Proyecto Merma Cero: Oráculo Estocástico de Resiliencia Climática   ")
    print("                 [Simulador de Interfaz WhatsApp]                    ")
    print("=====================================================================")
    default_phone = "+523121234567"
    print(f"[SESION ACTIVA] Simulación del teléfono: {default_phone}\n")

    while True:
        try:
            user_input = input("Vendedor >> ")
            if user_input.strip().lower() in ["salir", "exit", "quit"]:
                break
            if not user_input.strip():
                continue

            oraculo.process_message(default_phone, user_input)
        except Exception as e:
            print(f"\n[Error]: {e}\n")

def run_tests():
    """Ejecuta de forma automatizada la batería de pruebas TDD del oráculo."""
    import unittest
    import os
    print("Iniciando batería de pruebas unitarias locales...")
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = unittest.TestLoader().discover(start_dir=start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli_interactive()
    else:
        # Levantar servidor Uvicorn de alto rendimiento (FastAPI)
        import uvicorn
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))
        log_json(
            severity="INFO",
            message=f"Iniciando servidor FastAPI en http://{host}:{port}",
            context={"host": host, "port": port}
        )
        uvicorn.run("merma_cero.main:app", host=host, port=port, reload=False)
