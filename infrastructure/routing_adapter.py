# -*- coding: utf-8 -*-
"""Enrutador unificado de mensajería (Unified Messenger Router Adapter)."""
from merma_cero.application.ports import MessagePort

class UnifiedMessageAdapter(MessagePort):
    """Enrutador que decide si enviar el mensaje por Telegram o WhatsApp según el prefijo del receptor."""

    def __init__(self, whatsapp_adapter: MessagePort, telegram_adapter: MessagePort):
        self.whatsapp_adapter = whatsapp_adapter
        self.telegram_adapter = telegram_adapter

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Determina el canal y despacha el mensaje de forma transparente.
        
        Si el recipient_id empieza con 'telegram:', se enruta al adaptador de Telegram.
        De lo contrario, se despacha a través de WhatsApp (Twilio o Mock).
        """
        if recipient_id.startswith("telegram:"):
            return self.telegram_adapter.send_message(recipient_id, text)
        
        return self.whatsapp_adapter.send_message(recipient_id, text)
