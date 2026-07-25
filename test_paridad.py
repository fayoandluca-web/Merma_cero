# -*- coding: utf-8 -*-
"""Prueba de Paridad Matemática entre modelos.py (Python) y motor.js (Node.js).

Garantiza la correspondencia matemática numérica y de lógica de negocio (Zero Divergencia).
"""
import unittest
import json
import subprocess
import os
import sys

# Ajustar rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from merma_cero.domain.entities import WeatherState
from merma_cero.domain.models import DecayKinetics, GARCHVolatilityModel, KellyMermaSizer, MonteCarloMermaSimulator

class TestModelParity(unittest.TestCase):

    def setUp(self):
        """Prepara el entorno y verifica la existencia del motor JS."""
        self.js_motor_path = os.path.join(BASE_DIR, "motor.js")
        self.assertTrue(os.path.exists(self.js_motor_path), "Falta el archivo motor.js")

    def _run_js(self, payload):
        """Invoca a Node.js pasándole la petición JSON y obteniendo el resultado estructurado."""
        process = subprocess.Popen(
            ["node", self.js_motor_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        stdout, stderr = process.communicate(input=json.dumps(payload) + "\n")
        if process.returncode != 0:
            raise RuntimeError(f"Fallo en Node.js: {stderr.strip()}")
        
        response = json.loads(stdout.strip())
        if response.get("status") != "success":
            raise RuntimeError(f"Error devuelto por motor.js: {response.get('message')}")
        return response.get("data")

    def test_decay_rate_parity(self):
        """Compara DecayKinetics.calculate_decay_rate en todas las categorías."""
        categories = ["seafood", "flowers", "fruit_vegetables", "dairy", "generic"]
        temps = [15.5, 25.0, 38.2, 45.0]
        humidities = [0.20, 0.55, 0.85, 0.95]

        for cat in categories:
            for t in temps:
                for h in humidities:
                    weather = WeatherState(temperature=t, relative_humidity=h, precipitation_probability=0.1)
                    py_val = DecayKinetics.calculate_decay_rate(cat, weather)

                    payload = {
                        "action": "calculate_decay_rate",
                        "category": cat,
                        "temperature": t,
                        "relative_humidity": h
                    }
                    js_val = self._run_js(payload)

                    # Tolerancia de precisión flotante IEEE 754 de 1e-6
                    self.assertAlmostEqual(py_val, js_val, places=6, 
                                           msg=f"Discrepancia en decay_rate para {cat} a {t}°C, {h*100}% HR")

    def test_shelf_life_parity(self):
        """Compara DecayKinetics.calculate_shelf_life."""
        weather = WeatherState(temperature=32.0, relative_humidity=0.75, precipitation_probability=0.2)
        py_val = DecayKinetics.calculate_shelf_life("seafood", weather)

        payload = {
            "action": "calculate_shelf_life",
            "category": "seafood",
            "temperature": 32.0,
            "relative_humidity": 0.75
        }
        js_val = self._run_js(payload)

        self.assertAlmostEqual(py_val, js_val, places=6)

    def test_garch_volatility_parity(self):
        """Compara GARCHVolatilityModel.project_variance."""
        hist_temps = [20.0, 22.1, 23.5, 30.2, 35.0, 31.2, 28.5, 26.0, 24.1, 22.0]
        seasonal_means = [21.0, 21.0, 21.0, 21.0, 21.0, 21.0, 21.0, 21.0, 21.0, 21.0]

        py_var = GARCHVolatilityModel.project_variance(hist_temps, seasonal_means)

        payload = {
            "action": "project_variance",
            "historical_temperatures": hist_temps,
            "seasonal_means": seasonal_means
        }
        js_val = self._run_js(payload)

        self.assertAlmostEqual(py_var, js_val, places=6,
                               msg=f"Discrepancia en proyección de varianza GARCH")

    def test_kelly_sizer_parity(self):
        """Compara KellyMermaSizer.optimize_stock bajo condiciones estables y extremas."""
        # Test 1: Pescado con calor
        weather = WeatherState(temperature=35.0, relative_humidity=0.60, precipitation_probability=0.20)
        
        py_opt = KellyMermaSizer.optimize_stock("seafood", weather, 100.0, 30.0)
        
        payload = {
            "action": "optimize_stock",
            "category": "seafood",
            "temperature": 35.0,
            "relative_humidity": 0.60,
            "precipitation_probability": 0.20
        }
        js_opt = self._run_js(payload)
        
        self.assertEqual(py_opt, js_opt, f"Discrepancia en Kelly Sizer para pescado caliente")

        # Test 2: Flores con lluvia
        weather_rain = WeatherState(temperature=22.0, relative_humidity=0.85, precipitation_probability=0.80)
        py_opt_rain = KellyMermaSizer.optimize_stock("flowers", weather_rain, 100.0, 30.0)
        
        payload_rain = {
            "action": "optimize_stock",
            "category": "flowers",
            "temperature": 22.0,
            "relative_humidity": 0.85,
            "precipitation_probability": 0.80
        }
        js_opt_rain = self._run_js(payload_rain)
        
        self.assertEqual(py_opt_rain, js_opt_rain, f"Discrepancia en Kelly Sizer para flores con lluvia")

    def test_monte_carlo_parity(self):
        """Compara la distribución y CVaR del simulador Monte Carlo de 48h."""
        weather = WeatherState(temperature=30.0, relative_humidity=0.60, precipitation_probability=0.20)
        forecast_var = 1.5
        
        py_metrics = MonteCarloMermaSimulator.simulate_48h_decay(
            category="seafood",
            initial_weather=weather,
            forecast_variance=forecast_var,
            sim_samples=500,
            seed=42
        )
        
        payload = {
            "action": "simulate_48h_decay",
            "category": "seafood",
            "temperature": 30.0,
            "relative_humidity": 0.60,
            "precipitation_probability": 0.20,
            "forecast_variance": forecast_var,
            "sim_samples": 500,
            "seed": 42
        }
        js_metrics = self._run_js(payload)
        
        # Las simulaciones estocásticas con el mismo generador seedable Mulberry32
        # y Box-Muller deben dar resultados numéricos idénticos.
        self.assertAlmostEqual(py_metrics["expected_decay_48h"], js_metrics["expected_decay_48h"], places=6)
        self.assertAlmostEqual(py_metrics["var_95_decay_48h"], js_metrics["var_95_decay_48h"], places=6)
        self.assertAlmostEqual(py_metrics["cvar_95_decay_48h"], js_metrics["cvar_95_decay_48h"], places=6)

if __name__ == "__main__":
    unittest.main()
