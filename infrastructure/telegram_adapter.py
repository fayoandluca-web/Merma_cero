# -*- coding: utf-8 -*-
"""Adaptador de mensajería para Telegram (Telegram Bot API Adapter)."""
import os
import time
import json
import urllib.request
import urllib.parse
import sys
from typing import List, Tuple
from merma_cero.application.ports import MessagePort

class TelegramAdapter(MessagePort):
    """Adaptador que envía mensajes a través de Telegram usando HTTP POST nativo."""

    def __init__(self):
        self.outbox: List[Tuple[float, str, str]] = []
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")

    def _is_mock(self) -> bool:
        """Determina si debe operar en modo simulado/mock."""
        if not self.token or self.token.startswith("mock_"):
            return True
        return False

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Envía el mensaje a través de Telegram o lo imprime en consola si es simulado.
        
        Args:
            recipient_id: Identificador. Si empieza con 'telegram:', se remueve el prefijo.
            text: Contenido del mensaje.
        """
        now = time.time()
        self.outbox.append((now, recipient_id, text))

        chat_id = recipient_id
        if chat_id.startswith("telegram:"):
            chat_id = chat_id.replace("telegram:", "")

        if self._is_mock():
            # Modo Simulado (Mock)
            safe_text = text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            print(f"\n[TELEGRAM CLIENT] Mensaje enviado a {chat_id} a las {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}:")
            print("-" * 60)
            print(safe_text)
            print("-" * 60 + "\n")
            return True

        # Modo de Producción (Telegram Bot API)
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        # Telegram soporta formato Markdown
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                
                # Registrar el log de éxito en stderr
                log_entry = {
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                    "severity": "INFO",
                    "module": "merma_cero.infrastructure.telegram_adapter",
                    "message": "Mensaje enviado exitosamente vía Telegram Bot API",
                    "context": {"chat_id": chat_id, "message_id": res_json.get("result", {}).get("message_id")}
                }
                sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                return True
        except urllib.error.HTTPError as e:
            res_error = e.read().decode("utf-8") if e.fp else ""
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.telegram_adapter",
                "message": "Fallo HTTP al enviar mensaje por Telegram API",
                "context": {"chat_id": chat_id, "code": e.code, "error": res_error}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False
        except Exception as e:
            log_entry = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.telegram_adapter",
                "message": "Excepción no controlada en el adaptador de Telegram",
                "context": {"chat_id": chat_id, "error": str(e)}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            return False

    def clear_outbox(self) -> None:
        """Limpia el historial de salida."""
        self.outbox.clear()
