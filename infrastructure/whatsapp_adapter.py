# -*- coding: utf-8 -*-
"""Adaptador de mensajería conversacional (WhatsApp Cloud API Adapter)."""
import os
import time
import json
import urllib.request
import urllib.error
import sys
from typing import List, Tuple
from merma_cero.application.ports import MessagePort

class WhatsAppAdapter(MessagePort):
    """Adaptador híbrido que envía mensajes reales a la API de WhatsApp Cloud (Meta) o simula el envío localmente."""

    def __init__(self):
        self.outbox: List[Tuple[float, str, str]] = []
        # Cargar configuraciones de entorno
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    def _is_mock(self) -> bool:
        """Determina si debe operar en modo simulado/mock."""
        if not self.token or not self.phone_number_id:
            return True
        if self.token.startswith("mock_") or self.phone_number_id.startswith("mock_"):
            return True
        return False

    def send_message(self, phone: str, text: str) -> bool:
        """Envía el mensaje usando Meta Cloud API o simula la salida en consola si son credenciales mock."""
        now = time.time()
        self.outbox.append((now, phone, text))

        if self._is_mock():
            # Modo Simulado (Mock)
            safe_text = text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            print(f"\n[WHATSAPP CLIENT] Mensaje enviado a {phone} a las {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}:")
            print("-" * 60)
            print(safe_text)
            print("-" * 60 + "\n")
            return True

        # Modo de Producción (WhatsApp Cloud API de Meta)
        url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Limpiar el número de teléfono (debe tener código de país, formato E.164 sin el caracter '+')
        clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode("utf-8")
                # Registrar el log de éxito en stderr
                log_entry = {
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                    "severity": "INFO",
                    "module": "merma_cero.infrastructure.whatsapp_adapter",
                    "message": "Mensaje enviado exitosamente vía WhatsApp Cloud API",
                    "context": {"phone": phone, "response": json.loads(res_body)}
                }
                sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                return True
        except urllib.error.HTTPError as e:
            res_error = e.read().decode("utf-8") if e.fp else ""
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.whatsapp_adapter",
                "message": "Fallo HTTP al enviar mensaje por WhatsApp Cloud API",
                "context": {"phone": phone, "code": e.code, "error": res_error}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False
        except Exception as e:
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.whatsapp_adapter",
                "message": "Excepción no controlada en el adaptador de WhatsApp",
                "context": {"phone": phone, "error": str(e)}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False

    def clear_outbox(self) -> None:
        """Limpia el historial de salida."""
        self.outbox.clear()

# Alias para asegurar compatibilidad con código existente
WhatsAppMockAdapter = WhatsAppAdapter
