# -*- coding: utf-8 -*-
"""Suite de pruebas unitarias robusta bajo estándar x200 (pruebas_calidad.md)."""
import os
import unittest
import time
from unittest.mock import Mock, patch
from pydantic import ValidationError

from merma_cero.config import DATABASE_PATH
from merma_cero.domain.entities import WeatherState, Vendor
from merma_cero.domain.exceptions import InvalidInputError, SecurityViolationError
from merma_cero.domain.models import DecayKinetics, KellyMermaSizer
from merma_cero.application.use_cases import OraculoUseCase
from merma_cero.infrastructure.sqlite_repository import SQLiteVendorRepository
from merma_cero.infrastructure.weather_adapter import OpenMeteoAdapter
from merma_cero.infrastructure.whatsapp_adapter import WhatsAppMockAdapter

class TestMermaCeroSystem(unittest.TestCase):

    def setUp(self) -> None:
        """Inicialización de bases de datos y adaptadores en aislamiento."""
        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_database.db")
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        self.repo = SQLiteVendorRepository(db_path=self.test_db_path)
        self.whatsapp = WhatsAppMockAdapter()
        
        # Mock para Weather Service para evitar llamadas HTTP en tests unitarios normales
        self.mock_weather = Mock()
        self.mock_weather.get_weather.return_value = WeatherState(
            temperature=25.0,
            relative_humidity=0.60,
            precipitation_probability=0.10
        )

        # Mock para servicio de IA
        self.mock_ai = Mock()
        self.mock_ai.get_recommendation.return_value = "Acciones recomendadas con IA"
        
        self.use_case = OraculoUseCase(
            repository=self.repo,
            weather_service=self.mock_weather,
            message_sender=self.whatsapp,
            ai_service=self.mock_ai
        )

    def tearDown(self) -> None:
        """Limpieza de base de datos de pruebas."""
        try:
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
        except Exception:
            pass

    # =========================================================================
    # 1. HAPPY PATH (Casos de Éxito)
    # =========================================================================

    def test_implicit_registration_and_prediction_success(self) -> None:
        """Verifica que un vendedor nuevo se registre y reciba predicción de forma transparente."""
        phone = "+523121234567"
        # 1. Dar opt-in respondiendo "ACEPTO"
        optin_resp = self.use_case.process_message(phone, "ACEPTO")
        self.assertIn("activado Merma Cero", optin_resp)
        
        # 2. Enviar Nombre
        name_resp = self.use_case.process_message(phone, "Fabio Israel")
        self.assertIn("¿cuántos años tienes?", name_resp)
        
        # 3. Enviar Edad
        age_resp = self.use_case.process_message(phone, "17")
        self.assertIn("¿Cuánto tiempo llevas con tu negocio?", age_resp)
        
        # 4. Enviar Antigüedad
        years_resp = self.use_case.process_message(phone, "2")
        self.assertIn("Registro completado con éxito", years_resp)
        
        # 5. Enviar datos de producto y ubicación para obtener predicción
        message = "Hola, vendo pescado en lat 19.43 lon -99.13"
        response = self.use_case.process_message(phone, message)

        # Assert: Registro implícito exitoso en DB
        saved_vendor = self.repo.get_by_phone(phone)
        self.assertIsNotNone(saved_vendor)
        self.assertTrue(saved_vendor.opt_in)
        self.assertEqual(saved_vendor.inventory_category, "seafood")
        self.assertAlmostEqual(saved_vendor.latitude, 19.43)
        self.assertAlmostEqual(saved_vendor.longitude, -99.13)
        self.assertEqual(saved_vendor.age, 17)
        self.assertEqual(saved_vendor.business_years, 2.0)

        # Assert: Salida de mensajería generada
        self.assertIn("Pescados y Mariscos", response)
        self.assertIn("Vida de Anaquel", response)
        self.assertIn("Recomendación de Compra", response)

    def test_decay_kinetics_temperature_scaling(self) -> None:
        """Valida que la merma escale físicamente con temperaturas mayores (Efecto Arrhenius)."""
        weather_mild = WeatherState(temperature=20.0, relative_humidity=0.5, precipitation_probability=0.0)
        weather_hot = WeatherState(temperature=40.0, relative_humidity=0.5, precipitation_probability=0.0)

        rate_mild = DecayKinetics.calculate_decay_rate("seafood", weather_mild)
        rate_hot = DecayKinetics.calculate_decay_rate("seafood", weather_hot)

        # La tasa a 40°C debe ser significativamente mayor a la de 20°C
        self.assertGreater(rate_hot, rate_mild)

    def test_sizer_reduces_stock_on_extreme_weather(self) -> None:
        """Verifica que el optimizador reduzca el inventario ante riesgo térmico para mitigar merma."""
        weather_good = WeatherState(temperature=22.0, relative_humidity=0.50, precipitation_probability=0.0)
        weather_bad = WeatherState(temperature=38.0, relative_humidity=0.50, precipitation_probability=0.0)

        stock_good = KellyMermaSizer.optimize_stock("seafood", weather_good, 100.0, 30.0)
        stock_bad = KellyMermaSizer.optimize_stock("seafood", weather_bad, 100.0, 30.0)

        # Ante calor extremo y alta merma, el pedido óptimo recomendado debe decrecer
        self.assertLess(stock_bad, stock_good)

    # =========================================================================
    # 2. EDGE CASES (Casos Límite y Extremos)
    # =========================================================================

    def test_weather_state_clipping_extremes(self) -> None:
        """Verifica que temperaturas no físicas de entrada sean saneadas (clipping)."""
        # Entrada hostil de frío extremo y calor extremo
        weather_arctic = WeatherState(temperature=-15.0, relative_humidity=1.5, precipitation_probability=-0.5)
        
        # Deben ser restringidas a los límites configurados [0, 50] para temp y [0, 1] para prob
        self.assertEqual(weather_arctic.temperature, 0.0)
        self.assertEqual(weather_arctic.relative_humidity, 1.0)
        self.assertEqual(weather_arctic.precipitation_probability, 0.0)

    def test_vendor_invalid_coordinates(self) -> None:
        """Verifica que el validador de frontera rechace ubicaciones geográficas imposibles."""
        with self.assertRaises(InvalidInputError):
            Vendor(
                phone="+523121234567",
                latitude=95.0,  # Latitud inválida > 90
                longitude=-99.13,
                inventory_category="flowers",
                registration_timestamp=time.time(),
                rate_limit_last_update=time.time()
            )

    def test_vendor_invalid_phone(self) -> None:
        """Verifica el rechazo de identificadores telefónicos corruptos o intentos de inyección."""
        with self.assertRaises(InvalidInputError):
            Vendor(
                phone="numero-invalido-o-inyeccion;--",
                latitude=19.43,
                longitude=-99.13,
                inventory_category="flowers",
                registration_timestamp=time.time(),
                rate_limit_last_update=time.time()
            )

    # =========================================================================
    # 3. PROVOKED FAILURES (Fallos Provocados)
    # =========================================================================

    def test_database_corruption_recovery(self) -> None:
        """Verifica la autorecuperación del sistema ante un archivo JSON corrupto."""
        # Provocar corrupción del archivo escribiendo texto inválido
        with open(self.test_db_path, "w", encoding="utf-8") as f:
            f.write("CONTENIDO CORRUPTO NO VALIDO COMO JSON{{{")

        # El repositorio debe interceptar el error y levantar una estructura limpia
        corrupt_vendor = self.repo.get_by_phone("+523121234567")
        self.assertIsNone(corrupt_vendor)

    def test_rate_limiting_violation(self) -> None:
        """Verifica que el Token Bucket lance excepción ante spamming rápido."""
        phone = "+523129876543"
        
        # Pre-registrar con opt_in=True para saltar el flujo de opt-in en este test
        vendor = Vendor(
            phone=phone,
            latitude=19.4326,
            longitude=-99.1332,
            inventory_category="generic",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=True,
            name="Tío Chucho",
            age=45,
            business_years=10.0
        )
        self.repo.save(vendor)
        
        # Consumir la cuota inicial (10 tokens)
        for _ in range(10):
            self.use_case.process_message(phone, "hola")

        # La 11va llamada consecutiva en la misma ventana temporal debe denegarse
        with self.assertRaises(SecurityViolationError):
            self.use_case.process_message(phone, "hola")

    def test_weather_api_http_failure_fallback(self) -> None:
        """Verifica que si la API climática colapsa, el adaptador caiga en modo histórico estacional."""
        adapter = OpenMeteoAdapter()
        
        # Provocar fallo en la petición HTTP (URL rota)
        with patch("urllib.request.urlopen", side_effect=Exception("Timeout en servidor climático")):
            # Ejecutar consulta a latitud de Colima (19.0) en junio
            weather = adapter.get_weather(19.0, -104.0)
            
            # Debe retornar un estado de clima inferido funcional sin lanzar excepción
            self.assertIsNotNone(weather)
            self.assertGreater(weather.temperature, 20.0)  # Verano en Colima
            self.assertEqual(weather.relative_humidity, 0.75)  # Humedad de lluvias estimada

    def test_garch_volatility_projection(self) -> None:
        """Verifica que la proyección GARCH(1,1) responda coherentemente ante choques de volatilidad."""
        from merma_cero.domain.models import GARCHVolatilityModel
        hist_temps = [20.0, 21.0, 20.0, 22.0, 35.0]  # Choque de calor al final
        means = [20.0, 20.0, 20.0, 20.0, 20.0]
        
        # La varianza condicional proyectada ante un choque debe ser mayor a una serie totalmente estable
        var_shock = GARCHVolatilityModel.project_variance(hist_temps, means)
        
        hist_stable = [20.0, 20.0, 20.0, 20.0, 20.0]
        var_stable = GARCHVolatilityModel.project_variance(hist_stable, means)
        
        self.assertGreater(var_shock, var_stable)

    def test_monte_carlo_48h_decay(self) -> None:
        """Verifica los límites matemáticos del simulador estocástico Monte Carlo de 48h."""
        from merma_cero.domain.models import MonteCarloMermaSimulator
        initial_weather = WeatherState(temperature=30.0, relative_humidity=0.60, precipitation_probability=0.20)
        
        # Correr simulación estocástica
        metrics = MonteCarloMermaSimulator.simulate_48h_decay(
            category="seafood",
            initial_weather=initial_weather,
            forecast_variance=1.5
        )
        
        # Validar aserciones cuantitativas
        self.assertIn("expected_decay_48h", metrics)
        self.assertIn("var_95_decay_48h", metrics)
        self.assertIn("cvar_95_decay_48h", metrics)
        
        self.assertTrue(0.0 <= metrics["expected_decay_48h"] <= 1.0)
        self.assertGreaterEqual(metrics["var_95_decay_48h"], metrics["expected_decay_48h"])
        self.assertGreaterEqual(metrics["cvar_95_decay_48h"], metrics["var_95_decay_48h"])

    def test_proactive_alert_triggering(self) -> None:
        """Verifica que el escáner proactivo detecte riesgos climáticos y envíe alertas de forma selectiva."""
        # Configurar 2 vendedores en la DB
        vendor_alert = Vendor(
            phone="+523121111111",
            latitude=19.43,
            longitude=-99.13,
            inventory_category="seafood",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time()
        )
        vendor_no_alert = Vendor(
            phone="+523122222222",
            latitude=20.00,
            longitude=-100.00,
            inventory_category="flowers",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time()
        )
        self.repo.save(vendor_alert)
        self.repo.save(vendor_no_alert)

        # Configurar el mock de clima:
        # El primero tendrá clima de alerta (>30°C)
        # El segundo tendrá clima estable (25°C)
        def get_weather_mock(lat, lon):
            if lat == 19.43:
                return WeatherState(temperature=35.0, relative_humidity=0.50, precipitation_probability=0.10)
            return WeatherState(temperature=25.0, relative_humidity=0.60, precipitation_probability=0.10)
            
        self.mock_weather.get_weather.side_effect = get_weather_mock
        self.whatsapp.clear_outbox()

        # Act
        sent_phones = self.use_case.check_and_send_alerts()

        # Assert: Solo se debe enviar alerta al número en zona de riesgo (+523121111111)
        self.assertEqual(len(sent_phones), 1)
        self.assertEqual(sent_phones[0], "+523121111111")
        self.assertEqual(len(self.whatsapp.outbox), 1)
        self.assertIn("ALERTA CLIMÁTICA CRÍTICA", self.whatsapp.outbox[0][2])

    def test_gemini_adapter_fallback(self) -> None:
        """Verifica que el GeminiAIAdapter retorne recomendaciones deterministas si no hay llave de API."""
        from merma_cero.infrastructure.gemini_adapter import GeminiAIAdapter
        adapter = GeminiAIAdapter()
        
        # Con api_key vacía o mock, debe retornar las recomendaciones basadas en reglas
        weather_risk = WeatherState(temperature=35.0, relative_humidity=0.50, precipitation_probability=0.10)
        rec = adapter.get_recommendation("seafood", weather_risk, 3.0, 50.0)
        
        self.assertIsNotNone(rec)
        self.assertIn("OLA DE CALOR", rec)

    def test_opt_in_flow_new_vendor(self) -> None:
        """Verifica que un usuario nuevo reciba el mensaje de consentimiento de opt-in."""
        phone = "+523129990001"
        response = self.use_case.process_message(phone, "Hola, me interesa")
        
        # Debe solicitar la confirmación de opt-in y registrar al vendedor como inactivo (opt_in=False)
        self.assertIn("Aviso de Privacidad", response)
        self.assertIn("ACEPTO", response)
        
        vendor = self.repo.get_by_phone(phone)
        self.assertIsNotNone(vendor)
        self.assertFalse(vendor.opt_in)

    def test_opt_in_acceptance(self) -> None:
        """Verifica que al responder 'ACEPTO' se guarde el consentimiento y se confirme activación."""
        phone = "+523129990002"
        # Primer mensaje sin consentir
        self.use_case.process_message(phone, "Hola")
        
        # Responder con la palabra de opt-in
        response = self.use_case.process_message(phone, "ACEPTO")
        
        self.assertIn("activado Merma Cero", response)
        vendor = self.repo.get_by_phone(phone)
        self.assertTrue(vendor.opt_in)

    def test_opt_in_rejection_and_reminders(self) -> None:
        """Verifica que si no ha dado su consentimiento, cualquier otro mensaje reciba un recordatorio."""
        phone = "+523129990003"
        self.use_case.process_message(phone, "Hola") # Primer contacto solicita opt-in
        
        # Segundo contacto sin decir "ACEPTO"
        response = self.use_case.process_message(phone, "vendo limones en Colima")
        
        self.assertIn("confirma tu consentimiento", response)
        self.assertIn("ACEPTO", response)
        
        vendor = self.repo.get_by_phone(phone)
        self.assertFalse(vendor.opt_in)

    def test_calibration_feedback_accuracy_loop(self) -> None:
        """Verifica que la retroalimentación de acierto/error actualice el log e informe el ahorro."""
        phone = "+523129990004"
        # 1. Dar de alta y simular una predicción
        vendor = Vendor(
            phone=phone,
            latitude=19.43,
            longitude=-99.13,
            inventory_category="seafood",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=True,
            name="Tío Chucho",
            age=45,
            business_years=10.0
        )
        self.repo.save(vendor)
        self.use_case.process_message(phone, "vendo pescado en lat 19.43 lon -99.13")
        
        # 2. Responder "acierto"
        feedback_response = self.use_case.process_message(phone, "acierto")
        
        self.assertIn("Gracias por tu retroalimentación", feedback_response)
        self.assertIn("ahorro estimado", feedback_response)
        
        # Verificar estado persistido
        vendor = self.repo.get_by_phone(phone)
        # La última predicción de tipo 'inbound_request' debe tener 'prediction_accurate' = True
        last_log = vendor.message_history[-1] # El último log es el feedback o la predicción
        # Buscamos la última consulta de predicción para verificar el flag
        inbound_logs = [log for log in vendor.message_history if log.get("type") == "inbound_request"]
        self.assertTrue(inbound_logs[-1]["prediction_accurate"])
        self.assertIn("saved_cost_estimated", inbound_logs[-1]["metrics"])
        self.assertGreaterEqual(inbound_logs[-1]["metrics"]["saved_cost_estimated"], 0.0)

    def test_telegram_routing_adapter(self) -> None:
        """Verifica que el enrutador de mensajería distinga y dirija correctamente a Telegram o WhatsApp."""
        from merma_cero.infrastructure.routing_adapter import UnifiedMessageAdapter
        
        mock_wa = Mock()
        mock_tg = Mock()
        router = UnifiedMessageAdapter(whatsapp_adapter=mock_wa, telegram_adapter=mock_tg)
        
        # Enrutar a Telegram
        router.send_message("telegram:123456789", "Hola Bot")
        mock_tg.send_message.assert_called_once_with("telegram:123456789", "Hola Bot")
        mock_wa.send_message.assert_not_called()
        
        mock_tg.reset_mock()
        
        # Enrutar a WhatsApp
        router.send_message("+523121234567", "Hola WhatsApp")
        mock_wa.send_message.assert_called_once_with("+523121234567", "Hola WhatsApp")
        mock_tg.send_message.assert_not_called()

    def test_telegram_process_message_flow(self) -> None:
        """Verifica que el caso de uso acepte y procese flujos conversacionales con identificadores Telegram."""
        # Registrar y aceptar opt-in con un ID de Telegram
        telegram_id = "telegram:987654321"
        
        # Primer contacto: mensaje de bienvenida / opt-in
        optin_resp = self.use_case.process_message(telegram_id, "Hola")
        self.assertIn("Aviso de Privacidad", optin_resp)
        
        # Dar opt-in
        accept_resp = self.use_case.process_message(telegram_id, "ACEPTO")
        self.assertIn("Has activado Merma Cero", accept_resp)
        
        # Completar registro
        self.use_case.process_message(telegram_id, "Tío Chucho")
        self.use_case.process_message(telegram_id, "45")
        self.use_case.process_message(telegram_id, "10")
        
        # Solicitar predicción
        pred_resp = self.use_case.process_message(telegram_id, "vendo flores en lat 19.00 lon -104.00")
        self.assertIn("Flores y Plantas", pred_resp)
        self.assertIn("Recomendación de Compra", pred_resp)
        
        # Verificar guardado en repositorio
        vendor = self.repo.get_by_phone(telegram_id)
        self.assertIsNotNone(vendor)
        self.assertTrue(vendor.opt_in)
        self.assertEqual(vendor.inventory_category, "flowers")
        self.assertEqual(vendor.latitude, 19.00)
        self.assertEqual(vendor.longitude, -104.00)
        self.assertEqual(vendor.age, 45)
        self.assertEqual(vendor.business_years, 10.0)

    def test_send_fortnightly_survey(self) -> None:
        """Verifica el envío de la encuesta quincenal a usuarios con opt-in activo."""
        phone_optin = "+523121112222"
        phone_no_optin = "+523123334444"
        
        vendor1 = Vendor(
            phone=phone_optin,
            latitude=19.43,
            longitude=-99.13,
            inventory_category="seafood",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=True,
            name="Tío Chucho",
            age=45,
            business_years=10.0
        )
        vendor2 = Vendor(
            phone=phone_no_optin,
            latitude=19.43,
            longitude=-99.13,
            inventory_category="dairy",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=False,
            name="Tío Chucho",
            age=45,
            business_years=10.0
        )
        self.repo.save(vendor1)
        self.repo.save(vendor2)
        
        self.whatsapp.clear_outbox()
        sent = self.use_case.check_and_send_fortnightly_survey()
        
        # Debe enviar solo al que tiene opt-in
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0], phone_optin)
        self.assertEqual(len(self.whatsapp.outbox), 1)
        self.assertIn("Encuesta de Impacto", self.whatsapp.outbox[0][2])
        
        # El historial de mensajes del vendedor debe incluir la encuesta
        vendor = self.repo.get_by_phone(phone_optin)
        self.assertEqual(vendor.message_history[-1]["type"], "fortnightly_survey")

    def test_parse_survey_responses(self) -> None:
        """Verifica que las respuestas a la encuesta sean reconocidas e impacten en la bitácora."""
        phone = "+523125556666"
        vendor = Vendor(
            phone=phone,
            latitude=19.43,
            longitude=-99.13,
            inventory_category="flowers",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=True,
            name="Tío Chucho",
            age=45,
            business_years=10.0
        )
        self.repo.save(vendor)
        
        # Enviar la encuesta
        self.use_case.check_and_send_fortnightly_survey()
        
        # Probar diferentes variaciones de respuesta
        valid_inputs = ["A", "b", "opcion c", "opción a", "*b*", "*c)*"]
        expected_options = ["A", "B", "C", "A", "B", "C"]
        
        for inp, expected in zip(valid_inputs, expected_options):
            # Aseguramos que el último mensaje sea la encuesta (para simular el estado actual en cada ciclo)
            vendor = self.repo.get_by_phone(phone)
            vendor.message_history.append({
                "timestamp": time.time(),
                "type": "fortnightly_survey",
                "message_sent": "Encuesta de Impacto"
            })
            self.repo.save(vendor)
            
            response = self.use_case.process_message(phone, inp)
            self.assertIn("registrada en tu bitácora de impacto social", response)
            
            # Verificar base de datos
            updated_vendor = self.repo.get_by_phone(phone)
            last_log = updated_vendor.message_history[-1]
            self.assertEqual(last_log["type"], "survey_response")
            self.assertEqual(last_log["parsed_option"], expected)

    def test_survey_not_matching_fallthrough(self) -> None:
        """Verifica que si la respuesta no es una opción válida, continúe con el flujo estándar."""
        phone = "+523127778888"
        vendor = Vendor(
            phone=phone,
            latitude=19.43,
            longitude=-99.13,
            inventory_category="dairy",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=True,
            name="Tío Chucho",
            age=45,
            business_years=10.0
        )
        self.repo.save(vendor)
        
        # Enviar la encuesta
        self.use_case.check_and_send_fortnightly_survey()
        
        # Enviar un mensaje no relacionado (ej: "hola" o "quiero flores")
        response = self.use_case.process_message(phone, "quiero flores")
        
        # No debe ser una respuesta de encuesta de agradecimiento
        self.assertNotIn("estimación de ahorro quincenal ha sido registrada", response)
        # En su lugar, debe gatillar el oráculo (que responde con recomendación)
        self.assertIn("Vida de Anaquel", response)
        
        # El historial de mensajes debe reflejar una consulta ordinaria y no un survey_response
        updated_vendor = self.repo.get_by_phone(phone)
        last_log = updated_vendor.message_history[-1]
        self.assertEqual(last_log["type"], "inbound_request")

