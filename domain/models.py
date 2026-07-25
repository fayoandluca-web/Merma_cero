# -*- coding: utf-8 -*-
"""Modelos cuantitativos de cinética de merma y optimización estocástica de inventario."""
import numpy as np
from merma_cero.config import R_GAS_CONSTANT, INVENTORY_PARAMETERS, RISK_AERSION_LAMBDA
from merma_cero.domain.entities import WeatherState
from merma_cero.domain.exceptions import NumericalInstabilityError

class LCG:
    """Generador congruent lineal determinista para reproducibilidad multiplataforma."""
    def __init__(self, seed=42):
        self.state = seed if seed != 0 else 1

    def next_double(self) -> float:
        self.state = (48271 * self.state) % 2147483647
        return self.state / 2147483647.0

def box_muller(lcg: LCG) -> float:
    """Transformación Box-Muller utilizando LCG."""
    u1 = 0.0
    while u1 == 0.0:
        u1 = lcg.next_double()
    u2 = 0.0
    while u2 == 0.0:
        u2 = lcg.next_double()
    return float(np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2))


class DecayKinetics:
    """Calculador de la velocidad de descomposición de inventarios mediante la ecuación de Arrhenius."""

    @staticmethod
    def calculate_decay_rate(category: str, weather: WeatherState) -> float:
        """Calcula el coeficiente de velocidad de merma diaria K(T, H).
        
        Fórmula:
            K = K0 * exp(-Ea / (R * (T_celsius + 273.15))) * (1 + alpha * H)
        """
        params = INVENTORY_PARAMETERS.get(category, INVENTORY_PARAMETERS["generic"])
        
        # Conversión a Kelvin de la temperatura sanitizada de la entidad
        temp_kelvin = weather.temperature + 273.15
        if temp_kelvin <= 0.0:
            raise NumericalInstabilityError("Temperatura absoluta no física calculada.")

        # Componente Arrhenius de activación térmica
        exponent = -params["Ea"] / (R_GAS_CONSTANT * temp_kelvin)
        arrhenius_factor = params["K0"] * np.exp(exponent)
        
        # Modulador por humedad relativa
        humidity_factor = 1.0 + params["alpha"] * weather.relative_humidity
        
        # Velocidad de decaimiento final
        decay_rate = arrhenius_factor * humidity_factor
        
        # Estabilizador numérico: la velocidad de decaimiento no puede ser negativa
        # Cota inferior de 1e-6 (equivalente a 1 millón de días de vida de anaquel)
        return float(max(1e-6, decay_rate))

    @staticmethod
    def calculate_shelf_life(category: str, weather: WeatherState) -> float:
        """Retorna la vida de anaquel proyectada en días bajo el clima actual."""
        decay_rate = DecayKinetics.calculate_decay_rate(category, weather)
        return 1.0 / decay_rate

class GARCHVolatilityModel:
    """Modelo econométrico GARCH(1,1) para estimación y proyección de volatilidad climática."""

    @staticmethod
    def project_variance(
        historical_temperatures: list[float],
        seasonal_means: list[float],
        omega: float = 0.05,
        alpha: float = 0.15,
        beta: float = 0.80
    ) -> float:
        """Calcula la varianza condicional futura sigma^2_{t+1} basada en residuos históricos.
        
        Fórmula GARCH(1,1):
            sigma_t^2 = omega + alpha * epsilon_{t-1}^2 + beta * sigma_{t-1}^2
        """
        n = len(historical_temperatures)
        if n < 2 or len(seasonal_means) != n:
            # Retorna la varianza de largo plazo (incondicional) ante datos escasos
            denom = 1.0 - alpha - beta
            return omega / denom if denom > 0 else 1.0

        # Residuos de la serie temporal (anomalía de temperatura)
        residuals = [historical_temperatures[i] - seasonal_means[i] for i in range(n)]
        
        # Inicializar varianza condicional como la varianza de la muestra
        init_variance = float(np.var(residuals)) if len(residuals) > 0 else 1.0
        if init_variance <= 0:
            init_variance = 1.0

        current_variance = init_variance
        
        # Proceso de filtrado recursivo
        for i in range(1, n):
            epsilon_sq = residuals[i-1] ** 2
            current_variance = omega + alpha * epsilon_sq + beta * current_variance

        # Proyección un paso adelante (t + 1)
        last_epsilon_sq = residuals[-1] ** 2
        next_variance = omega + alpha * last_epsilon_sq + beta * current_variance
        return float(next_variance)

class KellyMermaSizer:
    """Optimizador estocástico de inventario basado en la maximización de la utilidad
    ajustada por riesgo (Mean-Variance Utility) bajo merma inducida por clima.
    """

    @staticmethod
    def optimize_stock(
        category: str,
        weather: WeatherState,
        base_demand_mean: float,
        base_demand_std: float,
        historical_temperatures: list[float] = None,
        seasonal_means: list[float] = None,
        sim_samples: int = 1000,
        seed: int = 42
    ) -> float:
        """Determina el volumen óptimo de compra S* que maximiza la utilidad esperada penalizada por volatilidad.
        
        Fórmulas del Oráculo:
            1. Modulación de la demanda por clima:
               Si llueve (precipitación > 0.4), la afluencia y demanda en economía informal cae.
               Si hace calor extremo, la demanda muta según el tipo de producto.
            2. Degradación del valor de rescate:
               salvage_effective = salvage_base * exp(-decay_rate * dt)
            3. Ajuste de Incertidumbre por GARCH(1,1):
               La volatilidad condicionada del clima escala la desviación estándar de la demanda.
            4. Maximización:
               S* = argmax_Q [ E[Profit(Q)] - lambda * Std(Profit(Q)) ]
        """
        params = INVENTORY_PARAMETERS.get(category, INVENTORY_PARAMETERS["generic"])
        price = params["default_price"]
        cost = params["default_cost"]
        salvage_base = params["default_salvage"]
        
        # 1. Calcular decaimiento térmico diario
        decay_rate = DecayKinetics.calculate_decay_rate(category, weather)
        
        # Salvamento degradado exponencialmente por descomposición en 1 día operacional (dt = 1)
        salvage_effective = salvage_base * np.exp(-decay_rate)
        
        # 2. Modular demanda promedio según clima
        weather_demand_multiplier = 1.0
        
        # Penalización por lluvia en la calle (economía ambulante fricción alta)
        if weather.precipitation_probability > 0.3:
            weather_demand_multiplier -= 0.35 * weather.precipitation_probability
            
        # Modulación térmica específica
        if category == "seafood":
            # El calor extremo desploma la demanda de mariscos por desconfianza higiénica
            if weather.temperature > 32.0:
                weather_demand_multiplier *= 0.60
        elif category == "flowers":
            # Olas de calor marchitan flores rápido, reduciendo el volumen de exhibición y ventas
            if weather.temperature > 30.0:
                weather_demand_multiplier *= 0.70
        elif category == "generic":
            if weather.temperature > 35.0:
                weather_demand_multiplier *= 0.80

        # Garantizar que el multiplicador no colapse a valores negativos
        weather_demand_multiplier = max(0.1, weather_demand_multiplier)
        
        adjusted_mean = base_demand_mean * weather_demand_multiplier
        adjusted_std = base_demand_std * max(0.5, weather_demand_multiplier)

        # 3. Modelado de Volatilidad Histórica GARCH(1,1) para Incertidumbre (Ley de Wilson)
        if historical_temperatures is None or len(historical_temperatures) < 2:
            # Generar historia sintética basada en la temperatura actual si no se provee
            # Simula una oscilación de ruido térmico normal
            historical_temperatures = [weather.temperature + float(np.sin(i)) for i in range(10)]
            seasonal_means = [weather.temperature for _ in range(10)]

        forecast_var = GARCHVolatilityModel.project_variance(historical_temperatures, seasonal_means)
        # Varianza de largo plazo de referencia
        long_term_var = 0.05 / (1.0 - 0.15 - 0.80)  # = 1.0
        
        # Escalar la incertidumbre de demanda proporcionalmente al desvío estándar condicional de GARCH
        volatility_multiplier = np.sqrt(forecast_var / long_term_var)
        adjusted_std = adjusted_std * max(0.5, min(2.5, volatility_multiplier))
        
        # Generar simulación determinista de demanda (reproducibilidad por TDD)
        lcg = LCG(seed)
        demands = []
        for _ in range(sim_samples):
            val = adjusted_mean + box_muller(lcg) * adjusted_std
            demands.append(max(0.0, val))
        
        # Grid-search unidimensional sobre cantidad de compra Q
        # Rango de búsqueda: desde 0 hasta el doble de la demanda esperada ajustada
        max_q_search = int(max(10.0, adjusted_mean * 2.5))
        q_grid = np.linspace(0.0, max_q_search, num=max_q_search + 1)
        
        best_q = 0.0
        max_utility = -1e15
        
        for q in q_grid:
            # Ventas reales obtenidas
            sales = np.minimum(q, demands)
            # Inventario sobrante
            surplus = np.maximum(0.0, q - demands)
            
            # Utilidad neta por escenario:
            # Profit = ventas * precio + excedente * salvamento_efectivo - compras * costo
            profits = (sales * price) + (surplus * salvage_effective) - (q * cost)
            
            # Estadísticas de cartera
            mean_profit = np.mean(profits)
            std_profit = np.std(profits)
            
            # Utilidad ajustada por riesgo (Fórmula del fondo de cobertura / Wilson Law)
            utility = mean_profit - RISK_AERSION_LAMBDA * std_profit
            
            if utility > max_utility:
                max_utility = utility
                best_q = q
                
        return float(best_q)

class MonteCarloMermaSimulator:
    """Simulador estocástico de Monte Carlo para proyectar la merma acumulada a 48 horas."""

    @staticmethod
    def simulate_48h_decay(
        category: str,
        initial_weather: WeatherState,
        forecast_variance: float,
        sim_samples: int = 1000,
        seed: int = 42
    ) -> dict[str, float]:
        """Proyecta la distribución acumulada de merma física sobre un horizonte de 2 días (48 horas).
        
        Mecánica:
            1. Simula 1000 trayectorias térmicas a 48h acoplando choques de volatilidad GARCH:
               T_{t+1} = T_t + eta * sqrt(forecast_variance)
            2. Evalúa la cinética de descomposición Arrhenius acumulada por día.
            3. Calcula estadísticas cuantitativas de riesgo (Expected Decay y CVaR 95%).
        """
        lcg = LCG(seed)
        decay_factors = []

        # Parámetros climáticos iniciales
        t0 = initial_weather.temperature
        h0 = initial_weather.relative_humidity
        p0 = initial_weather.precipitation_probability

        # Escala de volatilidad a partir de la varianza proyectada GARCH
        vol_scale = float(np.sqrt(forecast_variance))

        for _ in range(sim_samples):
            # Proyección Día 1: Clima inicial + shock moderado por horizonte
            shock_d1 = box_muller(lcg)
            t1 = float(np.clip(t0 + shock_d1 * vol_scale * 0.5, 0.0, 50.0))
            w1 = WeatherState(temperature=t1, relative_humidity=h0, precipitation_probability=p0)
            k1 = DecayKinetics.calculate_decay_rate(category, w1)

            # Proyección Día 2: Clima del día 1 + shock
            shock_d2 = box_muller(lcg)
            t2 = float(np.clip(t1 + shock_d2 * vol_scale * 0.5, 0.0, 50.0))
            w2 = WeatherState(temperature=t2, relative_humidity=h0, precipitation_probability=p0)
            k2 = DecayKinetics.calculate_decay_rate(category, w2)

            # Degradación total acumulada sobre 48 horas (horizonte dt = 2)
            accum_decay = 1.0 - float(np.exp(-(k1 + k2)))
            decay_factors.append(accum_decay)

        decay_factors.sort()
        mean_decay = sum(decay_factors) / sim_samples
        
        var_index = int(sim_samples * 0.95)
        var_95 = decay_factors[var_index]
        
        cvar_elements = decay_factors[var_index:]
        cvar_95 = sum(cvar_elements) / len(cvar_elements) if cvar_elements else var_95

        return {
            "expected_decay_48h": float(mean_decay),
            "var_95_decay_48h": float(var_95),
            "cvar_95_decay_48h": float(cvar_95)
        }

