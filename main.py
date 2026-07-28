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
    
    # 2. Sembrar la base de datos si está vacía
    try:
        from merma_cero.infrastructure.seeder import seed_database
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: seed_database(repo))
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
            
        log_json(
            severity="INFO",
            message="Petición recibida desde Telegram",
            context={"chat_id": chat_id},
            trace_id=trace_id
        )
        
        # Procesar la conversación de forma transparente
        response_text = oraculo.process_message(recipient_id, text_str)
        
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
    
    try:
        if "application/x-www-form-urlencoded" in content_type:
            # Parseo puro sin dependencia de python-multipart
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8")
            import urllib.parse
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

    # 2. Extraer teléfono y texto con soporte para Twilio, Meta y formato plano
    phone = None
    text = None
    
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
        else:
            # Formato plano de compatibilidad (Swagger / CLI / Simulador)
            phone = payload.get("phone")
            text = payload.get("text")
            
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
            context={"phone": phone_str},
            trace_id=trace_id
        )

        # Procesar caso de uso conversacional asíncrono
        response_text = oraculo.process_message(phone_str, text_str)
        
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
