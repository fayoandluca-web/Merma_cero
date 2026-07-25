# -*- coding: utf-8 -*-
"""CLI interactivo y administrativo para el oráculo Merma Cero.

Permite consultar predicciones, lanzar alertas proactivas, realizar simulaciones offline
de cinética Arrhenius / Monte Carlo, e iniciar el servidor.
"""
import sys
import os
import argparse

# Configurar ruta para imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merma_cero.domain.entities import WeatherState
from merma_cero.domain.models import DecayKinetics, KellyMermaSizer, MonteCarloMermaSimulator

def cmd_consultar(args):
    """Consulta directa del oráculo para un producto y ubicación."""
    from merma_cero.infrastructure.sqlite_repository import SQLiteVendorRepository
    from merma_cero.infrastructure.weather_adapter import OpenMeteoAdapter
    from merma_cero.infrastructure.whatsapp_adapter import WhatsAppMockAdapter
    from merma_cero.infrastructure.gemini_adapter import GeminiAIAdapter
    from merma_cero.application.use_cases import OraculoUseCase
    
    print(f"[*] Consultando oráculo para producto: {args.producto} en coordenadas ({args.lat}, {args.lon})")
    
    repo = SQLiteVendorRepository()
    weather_service = OpenMeteoAdapter()
    whatsapp = WhatsAppMockAdapter()
    ai_service = GeminiAIAdapter()
    
    use_case = OraculoUseCase(
        repository=repo,
        weather_service=weather_service,
        message_sender=whatsapp,
        ai_service=ai_service
    )
    
    phone = "+523120000000"
    message = f"Vendo {args.producto} en lat {args.lat} lon {args.lon}"
    response = use_case.process_message(phone, message)
    
    print("\n--- RESPUESTA DEL ORÁCULO ---")
    print(response)
    print("-----------------------------\n")

def cmd_alertas(args):
    """Lanza el envío masivo proactivo de alertas climáticas."""
    from merma_cero.infrastructure.sqlite_repository import SQLiteVendorRepository
    from merma_cero.infrastructure.weather_adapter import OpenMeteoAdapter
    from merma_cero.infrastructure.whatsapp_adapter import WhatsAppMockAdapter
    from merma_cero.infrastructure.gemini_adapter import GeminiAIAdapter
    from merma_cero.application.use_cases import OraculoUseCase

    print("[*] Iniciando escaneo y envío proactivo de alertas climáticas...")
    
    repo = SQLiteVendorRepository()
    weather_service = OpenMeteoAdapter()
    whatsapp = WhatsAppMockAdapter()
    ai_service = GeminiAIAdapter()
    
    use_case = OraculoUseCase(
        repository=repo,
        weather_service=weather_service,
        message_sender=whatsapp,
        ai_service=ai_service
    )
    
    sent_alerts = use_case.check_and_send_alerts()
    print(f"[+] Alertas enviadas con éxito a {len(sent_alerts)} vendedores:")
    for num in sent_alerts:
        print(f"  - {num}")

def cmd_simular(args):
    """Simulación offline de la cinética del producto y Monte Carlo a 48h."""
    weather = WeatherState(
        temperature=args.temp,
        relative_humidity=args.humedad,
        precipitation_probability=args.lluvia
    )
    
    decay_rate = DecayKinetics.calculate_decay_rate(args.producto, weather)
    shelf_life = DecayKinetics.calculate_shelf_life(args.producto, weather)
    
    stock_opt = KellyMermaSizer.optimize_stock(
        category=args.producto,
        weather=weather,
        base_demand_mean=100.0,
        base_demand_std=30.0
    )
    
    mc_metrics = MonteCarloMermaSimulator.simulate_48h_decay(
        category=args.producto,
        initial_weather=weather,
        forecast_variance=1.5
    )
    
    print(f"\n=======================================================")
    print(f"   SIMULACIÓN OFFLINE DE CINÉTICA — {args.producto.upper()}  ")
    print(f"=======================================================")
    print(f" Condición: Temp {args.temp}°C | Humedad {args.humedad*100:.0f}% | Lluvia {args.lluvia*100:.0f}%")
    print(f"-------------------------------------------------------")
    print(f" Tasa de descomposición Arrhenius (K): {decay_rate:.6f} / día")
    print(f" Vida de anaquel estimada:            {shelf_life:.2f} días")
    print(f" Compra óptima recomendada (Kelly):    {stock_opt:.1f}% de la demanda")
    print(f"-------------------------------------------------------")
    print(f" Simulación Monte Carlo a 48 horas:")
    print(f"   - Merma acumulada esperada:        {mc_metrics['expected_decay_48h']*100:.2f}%")
    print(f"   - Pérdida al 95% de confianza (VaR): {mc_metrics['var_95_decay_48h']*100:.2f}%")
    print(f"   - Merma esperada en cola (CVaR 95%): {mc_metrics['cvar_95_decay_48h']*100:.2f}%")
    print(f"=======================================================\n")

def cmd_servidor(args):
    """Inicia el servidor backend FastAPI de producción."""
    import uvicorn
    from dotenv import load_dotenv
    
    load_dotenv()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"[+] Iniciando servidor Uvicorn en http://{host}:{port}...")
    uvicorn.run("merma_cero.main:app", host=host, port=port, reload=args.reload)

def cmd_pruebas(args):
    """Ejecuta la suite de pruebas unitarias locales."""
    import unittest
    print("[*] Iniciando suite de pruebas unitarias y de integración de Merma Cero...")
    from merma_cero.test_merma_cero import TestMermaCeroSystem
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMermaCeroSystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

def main():
    parser = argparse.ArgumentParser(
        description="CLI de Control Administrativo y Simulación - Proyecto Merma Cero"
    )
    subparsers = parser.add_subparsers(title="subcomandos", dest="comando", required=True)
    
    # Subcomando consultar
    p_consultar = subparsers.add_parser("consultar", help="Consulta directa del oráculo para un producto")
    p_consultar.add_argument("--producto", choices=["seafood", "flowers", "fruit_vegetables", "dairy", "generic"], required=True, help="Categoría de producto")
    p_consultar.add_argument("--lat", type=float, default=19.4326, help="Latitud geográfica de consulta")
    p_consultar.add_argument("--lon", type=float, default=-99.1332, help="Longitud geográfica de consulta")
    p_consultar.set_defaults(func=cmd_consultar)
    
    # Subcomando alertas
    p_alertas = subparsers.add_parser("alertas", help="Envía alertas climáticas proactivas a vendedores registrados")
    p_alertas.set_defaults(func=cmd_alertas)
    
    # Subcomando simular
    p_simular = subparsers.add_parser("simular", help="Ejecuta simulación offline de cinética y Monte Carlo")
    p_simular.add_argument("--producto", choices=["seafood", "flowers", "fruit_vegetables", "dairy", "generic"], required=True, help="Categoría de producto")
    p_simular.add_argument("--temp", type=float, required=True, help="Temperatura ambiente en °C")
    p_simular.add_argument("--humedad", type=float, required=True, help="Humedad relativa en fracción [0.0 - 1.0]")
    p_simular.add_argument("--lluvia", type=float, default=0.0, help="Probabilidad de lluvia en fracción [0.0 - 1.0]")
    p_simular.set_defaults(func=cmd_simular)
    
    # Subcomando servidor
    p_servidor = subparsers.add_parser("servidor", help="Levanta el servidor web FastAPI")
    p_servidor.add_argument("--reload", action="store_true", help="Habilita auto-recarga del código (desarrollo)")
    p_servidor.set_defaults(func=cmd_servidor)
    
    # Subcomando pruebas
    p_pruebas = subparsers.add_parser("pruebas", help="Ejecuta la suite de pruebas unitarias completas")
    p_pruebas.set_defaults(func=cmd_pruebas)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
