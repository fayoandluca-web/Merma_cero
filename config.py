# -*- coding: utf-8 -*-
"""Configuración global y constantes físicas para el Proyecto Merma Cero."""
import os

# Rutas de almacenamiento
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.json")
DATABASE_URL = os.getenv("DATABASE_URL")


# Constantes Físicas para Cinética de Degradación
R_GAS_CONSTANT = 8.314  # Constante universal de los gases (J / mol*K)

# Parámetros por Categoría de Inventario Perecedero (Cinética Arrhenius)
# Ea: Energía de activación (J/mol) - sensibilidad a la temperatura
# K0: Factor pre-exponencial de velocidad de merma base (escala arbitraria de decaimiento diario)
# Alpha: Coeficiente de aceleración por humedad relativa (adimensional)
# DefaultPrice: Precio de venta unitario típico (pesos)
# DefaultCost: Costo de compra unitario típico (pesos)
# DefaultSalvage: Valor de rescate antes de merma total (pesos)
BASE_PARAMS = {
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
        "alpha": -0.4,
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

BASE_PRODUCTS = {
    "seafood": ["pescado", "camaron", "pulpo", "ostion", "jaiba", "calamar", "salmon", "atun", "mojarra", "huachinango", "robalo", "cazon", "sardina", "langosta", "marisco"],
    "flowers": ["rosa", "clavel", "tulipan", "girasol", "orquidea", "margarita", "lilio", "crisantemo", "gladiola", "nube", "gerbera", "alcatraz", "azucena", "clavelina", "flor"],
    "fruit_vegetables": ["manzana", "platano", "limon", "aguacate", "jitomate", "cebolla", "papa", "zanahoria", "naranja", "uva", "fresa", "sandia", "melon", "papaya", "pina", "chile", "calabaza", "lechuga", "pepino", "ajo", "brocoli", "coliflor", "espinaca", "apio", "cilantro", "perejil", "ejote", "nopal", "mango", "guayaba", "ciruela", "durazno", "mandarina", "pera", "toronja", "mamey", "tamarindo", "jicama", "betabel", "rabano", "camote", "champinon", "elote", "chicharo", "haba", "fruta", "verdura", "legumbre", "baya", "hoja"],
    "dairy": ["leche", "queso", "yogurt", "mantequilla", "crema", "requeson", "panela", "oaxaca", "manchego", "chihuahua", "asadero", "cotija", "parmesano", "gouda", "lacteo"],
    "generic": ["abarrotes", "semillas", "chiles_secos", "dulces", "especias"]
}

VARIETIES = ["estandar", "premium", "organico", "economico", "importado", "local", "fresco", "maduro", "silvestre", "a_granel"]

INVENTORY_PARAMETERS = {}

for cat_group, bases in BASE_PRODUCTS.items():
    for base in bases:
        for variety in VARIETIES:
            cat_key = f"{base}_{variety}"
            params = dict(BASE_PARAMS[cat_group])
            if variety == "premium":
                params["default_price"] *= 1.5
                params["default_cost"] *= 1.3
            elif variety == "organico":
                params["default_price"] *= 1.8
                params["default_cost"] *= 1.5
                params["Ea"] *= 0.95
            elif variety == "economico":
                params["default_price"] *= 0.7
                params["default_cost"] *= 0.7
            elif variety == "importado":
                params["default_price"] *= 1.4
                params["default_cost"] *= 1.4
            elif variety == "fresco":
                params["K0"] *= 0.8
            elif variety == "maduro":
                params["K0"] *= 1.5
                params["default_price"] *= 0.8
            params["default_price"] = round(params["default_price"], 2)
            params["default_cost"] = round(params["default_cost"], 2)
            params["default_salvage"] = round(params["default_salvage"], 2)
            INVENTORY_PARAMETERS[cat_key] = params

for k, v in BASE_PARAMS.items():
    INVENTORY_PARAMETERS[k] = dict(v)

def get_category_name_es(category_key: str) -> str:
    """Devuelve la traducción dinámica y limpia de la categoría."""
    if category_key in BASE_PARAMS:
        return {
            "seafood": "Pescados y Mariscos",
            "flowers": "Flores y Plantas",
            "fruit_vegetables": "Frutas y Verduras",
            "dairy": "Lácteos y Quesos",
            "generic": "Mercancía General"
        }.get(category_key, "Mercancía General")
    parts = category_key.split("_")
    name = " ".join([p.capitalize() for p in parts])
    words = name.split(" ")
    if len(words) > 0:
        base_word = words[0]
        if not base_word.endswith('s'):
            if base_word[-1] in 'aeiou':
                words[0] = base_word + 's'
            else:
                words[0] = base_word + 'es'
        name = " ".join(words)
    return name

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
