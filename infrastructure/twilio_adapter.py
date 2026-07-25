# -*- coding: utf-8 -*-
"""Adaptador de mensajería para Twilio (Twilio WhatsApp API Adapter)."""
import os
import time
import json
import urllib.request
import urllib.parse
import base64
import sys
from typing import List, Tuple
from merma_cero.application.ports import MessagePort

class TwilioAdapter(MessagePort):
    """Adaptador que envía mensajes usando la API de WhatsApp de Twilio o los simula localmente."""

    def __init__(self):
        self.outbox: List[Tuple[float, str, str]] = []
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER") # e.g. whatsapp:+14155238886

    def _is_mock(self) -> bool:
        """Determina si debe operar en modo simulado/mock."""
        if not self.account_sid or not self.auth_token or not self.from_number:
            return True
        if self.account_sid.startswith("mock_") or self.auth_token.startswith("mock_"):
            return True
        return False

    def send_message(self, phone: str, text: str) -> bool:
        """Envía el mensaje de WhatsApp a través del sandbox de Twilio o lo imprime en consola."""
        now = time.time()
        self.outbox.append((now, phone, text))

        if self._is_mock():
            # Modo Simulado (Mock)
            safe_text = text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            print(f"\n[TWILIO CLIENT] Mensaje enviado a {phone} a las {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}:")
            print("-" * 60)
            print(safe_text)
            print("-" * 60 + "\n")
            return True

        # Modo de Producción (Twilio WhatsApp API)
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        # Dar formato de WhatsApp de Twilio al teléfono del destinatario
        to_number = phone
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
            
        # Dar formato al número remitente
        from_number = self.from_number
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"

        data = {
            "From": from_number,
            "To": to_number,
            "Body": text
        }

        # Codificar datos form-urlencoded para Twilio
        payload = urllib.parse.urlencode(data).encode("utf-8")
        
        # Credenciales de Basic Auth
        auth_str = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_str.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Authorization", f"Basic {auth_base64}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode("utf-8")
                # Registrar el log de éxito en stderr
                log_entry = {
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                    "severity": "INFO",
                    "module": "merma_cero.infrastructure.twilio_adapter",
                    "message": "Mensaje enviado exitosamente vía Twilio WhatsApp API",
                    "context": {"phone": phone, "sid": json.loads(res_body).get("sid")}
                }
                sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                return True
        except urllib.error.HTTPError as e:
            res_error = e.read().decode("utf-8") if e.fp else ""
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.twilio_adapter",
                "message": "Fallo HTTP al enviar mensaje por Twilio API",
                "context": {"phone": phone, "code": e.code, "error": res_error}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False
        except Exception as e:
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.twilio_adapter",
                "message": "Excepción no controlada en el adaptador de Twilio",
                "context": {"phone": phone, "error": str(e)}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False

    def clear_outbox(self) -> None:
        """Limpia el historial de salida."""
        self.outbox.clear()
