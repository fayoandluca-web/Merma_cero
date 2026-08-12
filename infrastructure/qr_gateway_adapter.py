# -*- coding: utf-8 -*-
"""Adaptador de mensajería para pasarela QR de WhatsApp Web (Local QR Gateway Adapter)."""
import urllib.request
import json
import sys
import time
from merma_cero.application.ports import MessagePort

class QRGatewayAdapter(MessagePort):
    """Adaptador que envía mensajes a través de la pasarela local de WhatsApp Web (QR)."""

    def __init__(self, gateway_url: str = "http://localhost:3000/send"):
        self.gateway_url = gateway_url

    def send_message(self, phone: str, text: str) -> bool:
        """Envía el mensaje haciendo una petición POST a la pasarela Node.js local."""
        data = {
            "to": phone,
            "body": text
        }
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(self.gateway_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")

        now = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode("utf-8")
                log_entry = {
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                    "severity": "INFO",
                    "module": "merma_cero.infrastructure.qr_gateway_adapter",
                    "message": "Mensaje enviado exitosamente vía QR Gateway",
                    "context": {"phone": phone, "response": json.loads(res_body)}
                }
                sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                return True
        except Exception as e:
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.qr_gateway_adapter",
                "message": "Fallo al enviar mensaje por QR Gateway",
                "context": {"phone": phone, "error": str(e)}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False
