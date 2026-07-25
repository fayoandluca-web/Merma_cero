# -*- coding: utf-8 -*-
"""Script de sondeo (polling) local para el bot de Telegram de Merma Cero.

Permite pruebas de desarrollo local sin requerir túnel HTTPS (ngrok) ni despliegue.
"""
import os
import sys
import time
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Cargar variables
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LOCAL_WEBHOOK_URL = "http://127.0.0.1:8000/telegram/webhook"

def run_polling():
    if not TOKEN or TOKEN.startswith("mock_"):
        print("[-] Error: TELEGRAM_BOT_TOKEN no configurado en el archivo .env.")
        print("Por favor, crea un bot en Telegram usando @BotFather y agrega el token al .env.")
        sys.exit(1)

    print("[*] Iniciando sondeo local para el bot de Telegram...")
    print(f"[*] Enviando eventos a: {LOCAL_WEBHOOK_URL}")
    print("[*] Envía un mensaje a tu bot en Telegram para probar. Presiona CTRL+C para detener.")

    # Desactivar webhook si estaba configurado, para poder usar getUpdates
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=5)
    except Exception as e:
        print(f"[!] Advertencia al intentar limpiar webhook anterior: {e}")

    offset = 0
    while True:
        try:
            # Obtener actualizaciones acumuladas
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=10&offset={offset}"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                
                if not data.get("ok"):
                    print(f"[-] Error devuelto por Telegram API: {data}")
                    time.sleep(5)
                    continue
                
                updates = data.get("result", [])
                for update in updates:
                    update_id = update.get("update_id")
                    offset = update_id + 1  # Incrementar offset para no duplicar ingestas
                    
                    # Reenviar la actualización al webhook local de FastAPI
                    print(f"[+] Reenviando evento {update_id} al servidor local...")
                    
                    payload = json.dumps(update).encode("utf-8")
                    webhook_req = urllib.request.Request(LOCAL_WEBHOOK_URL, data=payload, method="POST")
                    webhook_req.add_header("Content-Type", "application/json")
                    
                    try:
                        with urllib.request.urlopen(webhook_req, timeout=5) as webhook_resp:
                            res_body = webhook_resp.read().decode("utf-8")
                            print(f"[OK] Servidor local respondió: {res_body.strip()}")
                    except urllib.error.HTTPError as he:
                        print(f"[-] Servidor local devolvió error {he.code}: {he.read().decode('utf-8')}")
                    except Exception as le:
                        print(f"[-] No se pudo conectar con el servidor local FastAPI: {le}")
                        print("Asegúrate de que 'python main.py' esté corriendo en el puerto 8000.")

        except KeyboardInterrupt:
            print("\n[*] Deteniendo sondeo local.")
            break
        except Exception as e:
            print(f"[-] Error de conexión en el bucle de sondeo: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_polling()
