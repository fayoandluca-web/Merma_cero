# -*- coding: utf-8 -*-
"""Adaptador de Inteligencia Artificial utilizando la API de Gemini (REST)."""
import os
import json
import urllib.request
import urllib.error
import sys
from merma_cero.application.ports import AIServicePort
from merma_cero.domain.entities import WeatherState

class GeminiAIAdapter(AIServicePort):
    """Adaptador para el servicio de recomendaciones basadas en Inteligencia Artificial (Gemini)."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def _get_rule_based_fallback(
        self,
        category: str,
        weather: WeatherState,
        shelf_life: float,
        optimal_purchase_pct: float
    ) -> str:
        """Fallback determinista basado en reglas si la IA no está disponible (Fricción Cero / Falkland Law)."""
        mitigation_tips = []
        
        # Traducir categoría para coherencia
        cat_es = {
            "seafood": "pescados y mariscos",
            "flowers": "flores y plantas",
            "fruit_vegetables": "frutas y verduras",
            "dairy": "lácteos y quesos",
            "generic": "mercancía"
        }.get(category, "mercancía")

        if weather.temperature > 30.0:
            if category == "seafood":
                mitigation_tips.append("⚠️ OLA DE CALOR: Duplica la cama de hielo molido. No expongas al sol directo.")
            elif category == "flowers":
                mitigation_tips.append("⚠️ CALOR EXTREMO: Rocía agua helada en tallos. Mantén recipientes a la sombra.")
            else:
                mitigation_tips.append(f"⚠️ TEMPERATURA ALTA: Coloca lonas reflectantes y reduce la exposición física de tu {cat_es}.")
        
        if weather.precipitation_probability > 0.4:
            mitigation_tips.append("🌧️ ALTA PROBABILIDAD DE LLUVIA: La afluencia peatonal bajará. Protege tu mercancía con plástico.")
        
        if not mitigation_tips:
            mitigation_tips.append("☀️ Clima estable para exhibición en vía pública.")

        return "\n".join(mitigation_tips)

    def get_recommendation(
        self,
        category: str,
        weather: WeatherState,
        shelf_life: float,
        optimal_purchase_pct: float
    ) -> str:
        """Consulta la API de Gemini para obtener consejos accionables personalizados o cae en el fallback."""
        if not self.api_key or self.api_key.startswith("mock_"):
            return self._get_rule_based_fallback(category, weather, shelf_life, optimal_purchase_pct)

        # Configuración de llamada a Gemini API (Modelo Gemini 2.5 Flash por REST)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }

        cat_es = {
            "seafood": "pescados y mariscos",
            "flowers": "flores y plantas",
            "fruit_vegetables": "frutas y verduras",
            "dairy": "lácteos y quesos",
            "generic": "mercancía general"
        }.get(category, "mercancía general")

        prompt = (
            f"Eres el Oráculo de Resiliencia Climática para pequeños comerciantes.\n"
            f"Giro del negocio: {cat_es}.\n"
            f"Condiciones climáticas pronosticadas:\n"
            f"- Temperatura: {weather.temperature:.1f}°C\n"
            f"- Humedad relativa: {weather.relative_humidity * 100:.0f}%\n"
            f"- Probabilidad de lluvia: {weather.precipitation_probability * 100:.0f}%\n"
            f"Vida de anaquel física estimada: {shelf_life:.1f} días.\n"
            f"Sugerencia de compra: Adquirir el {optimal_purchase_pct:.0f}% del volumen habitual.\n\n"
            f"Genera una recomendación muy breve, sumamente práctica y en español mexicano sencillo. "
            f"Da 1 o 2 acciones concretas para proteger su {cat_es} y mitigar el desperdicio según el clima de hoy. "
            f"Sé empático y ve directo al grano. Máximo 150 caracteres. No agregues introducciones ni saludos."
        )

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=7) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                
                # Extraer texto de la respuesta
                candidates = res_json.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        recommendation = parts[0].get("text", "").strip()
                        if recommendation:
                            return recommendation

                # Log de advertencia si la estructura de respuesta es inesperada
                log_entry = {
                    "timestamp": json.loads(res_body).get("timestamp", ""),
                    "severity": "WARN",
                    "module": "merma_cero.infrastructure.gemini_adapter",
                    "message": "Estructura inesperada de Gemini API. Usando fallback.",
                    "context": {"response": res_json}
                }
                sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except urllib.error.HTTPError as e:
            res_error = e.read().decode("utf-8") if e.fp else ""
            log_entry = {
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.gemini_adapter",
                "message": "Fallo HTTP al llamar a Gemini API",
                "context": {"code": e.code, "error": res_error}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            log_entry = {
                "severity": "ERROR",
                "module": "merma_cero.infrastructure.gemini_adapter",
                "message": "Fallo no controlado al conectar con Gemini API",
                "context": {"error": str(e)}
            }
            sys.stderr.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # Fallback si falla la llamada
        return self._get_rule_based_fallback(category, weather, shelf_life, optimal_purchase_pct)
