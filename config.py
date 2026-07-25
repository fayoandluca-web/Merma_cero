# -*- coding: utf-8 -*-
"""Configuración global y constantes físicas para el Proyecto Merma Cero."""
import os

# Rutas de almacenamiento
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.json")

# Constantes Físicas para Cinética de Degradación
R_GAS_CONSTANT = 8.314  # Constante universal de los gases (J / mol*K)

# Parámetros por Categoría de Inventario Perecedero (Cinética Arrhenius)
# Ea: Energía de activación (J/mol) - sensibilidad a la temperatura
# K0: Factor pre-exponencial de velocidad de merma base (escala arbitraria de decaimiento diario)
# Alpha: Coeficiente de aceleración por humedad relativa (adimensional)
# DefaultPrice: Precio de venta unitario típico (pesos)
# DefaultCost: Costo de compra unitario típico (pesos)
# DefaultSalvage: Valor de rescate antes de merma total (pesos)
INVENTORY_PARAMETERS = {
    "seafood": {
        "Ea": 65000.0,
        "K0": 2.5e10,
        "alpha": 1.2,
        "default_price": 120.0,
        "default_cost": 70.0,
        "default_salvage": 10.0,
    },
    "flowers": {
        "Ea": 55000.0,
        "K0": 8.0e8,
        "alpha": -0.4,  # La humedad alta disminuye la marchitez en flores
        "default_price": 50.0,
        "default_cost": 20.0,
        "default_salvage": 5.0,
    },
    "fruit_vegetables": {
        "Ea": 48000.0,
        "K0": 4.5e7,
        "alpha": 0.8,
        "default_price": 40.0,
        "default_cost": 18.0,
        "default_salvage": 4.0,
    },
    "dairy": {
        "Ea": 72000.0,
        "K0": 5.0e11,
        "alpha": 0.5,
        "default_price": 35.0,
        "default_cost": 22.0,
        "default_salvage": 2.0,
    },
    "generic": {
        "Ea": 50000.0,
        "K0": 1.0e8,
        "alpha": 0.5,
        "default_price": 50.0,
        "default_cost": 25.0,
        "default_salvage": 5.0,
    }
}

# Parámetros del Sizer (Optimización de Inventario)
RISK_AERSION_LAMBDA = 0.5  # Penalización de varianza del beneficio (tipo Markowitz/VaR)
DEFAULT_DEMAND_MEAN = 100.0
DEFAULT_DEMAND_STD = 30.0

# Límites de Seguridad de Ingesta (Murphy & Blindaje)
MAX_TEMP_CLIPPING = 50.0   # °C máximo
MIN_TEMP_CLIPPING = 0.0    # °C mínimo
MAX_HUMIDITY_CLIPPING = 1.0  # Humedad relativa máxima (100%)
MIN_HUMIDITY_CLIPPING = 0.0  # Humedad relativa mínima (0%)

# Rate Limiting (Token Bucket)
RATE_LIMIT_MAX_TOKENS = 10  # Máximo de solicitudes acumulables
RATE_LIMIT_REFILL_RATE = 1.0 / 3600.0  # Refill de 1 token por hora (en segundos)
