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

giros = {
    "carniceria": ("Carnicería", "seafood", 150.0, 90.0, 15.0),
    "floreria": ("Florería", "flowers", 60.0, 25.0, 5.0),
    "fruteria": ("Frutería", "fruit_vegetables", 45.0, 20.0, 4.0),
    "verduleria": ("Verdulería", "fruit_vegetables", 35.0, 15.0, 3.0),
    "cremeria": ("Cremería", "dairy", 50.0, 30.0, 5.0),
    "dulceria": ("Dulcería", "generic", 30.0, 15.0, 3.0),
    "ferreteria": ("Ferretería", "generic", 80.0, 50.0, 10.0),
    "abarrotes": ("Abarrotes", "generic", 25.0, 15.0, 2.0),
    "pescaderia": ("Pescadería", "seafood", 140.0, 80.0, 10.0),
    "polleria": ("Pollería", "seafood", 90.0, 55.0, 8.0),
    "panaderia": ("Panadería", "dairy", 20.0, 10.0, 1.0),
    "reposteria": ("Repostería", "dairy", 70.0, 40.0, 5.0),
    "tiendita": ("Tiendita", "generic", 25.0, 15.0, 2.0),
    "queseria": ("Quesería", "dairy", 80.0, 48.0, 8.0),
    "semilleria": ("Semillería", "fruit_vegetables", 40.0, 20.0, 4.0),
    "hierberia": ("Hierbería", "flowers", 35.0, 15.0, 2.0),
    "vivero": ("Vivero", "flowers", 55.0, 25.0, 5.0),
    "jugueria": ("Juguería", "fruit_vegetables", 30.0, 12.0, 2.0),
    "rosticeria": ("Rosticería", "seafood", 110.0, 70.0, 10.0),
    "marisqueria": ("Marisquería", "seafood", 160.0, 95.0, 15.0),
    "taqueria": ("Taquería", "seafood", 45.0, 22.0, 3.0),
    "torteria": ("Tortería", "seafood", 55.0, 28.0, 4.0),
    "pizzeria": ("Pizzería", "dairy", 120.0, 60.0, 10.0),
    "fondita": ("Fondita", "generic", 65.0, 35.0, 5.0),
    "cafeteria": ("Cafetería", "generic", 50.0, 20.0, 3.0),
    "heladeria": ("Heladería", "dairy", 40.0, 20.0, 3.0),
    "churreria": ("Churrería", "generic", 25.0, 10.0, 1.0),
    "pasteleria": ("Pastelería", "dairy", 150.0, 85.0, 10.0),
    "paleteria": ("Paletería", "dairy", 25.0, 12.0, 2.0),
    "hamburgueseria": ("Hamburguesería", "seafood", 85.0, 45.0, 5.0),
    "cerveceria": ("Cervecería", "generic", 60.0, 35.0, 5.0),
    "licoreria": ("Licorería", "generic", 180.0, 120.0, 20.0),
    "tienda_de_mascotas": ("Tienda de Mascotas", "generic", 120.0, 75.0, 15.0),
    "papeleria": ("Papelería", "generic", 15.0, 7.0, 1.0),
    "jugueteria": ("Juguetería", "generic", 250.0, 150.0, 30.0),
    "zapateria": ("Zapatería", "generic", 450.0, 250.0, 50.0),
    "boutique": ("Boutique", "generic", 350.0, 180.0, 30.0),
    "merceria": ("Mercería", "generic", 15.0, 7.0, 1.0),
    "recauderia": ("Recaudería", "fruit_vegetables", 30.0, 15.0, 2.0),
    "salchichoneria": ("Salchichonería", "dairy", 90.0, 55.0, 8.0),
    "charcuteria": ("Charcutería", "dairy", 180.0, 110.0, 15.0),
    "puesto_de_carnitas": ("Puesto de Carnitas", "seafood", 110.0, 65.0, 8.0),
    "birrieria": ("Birriería", "seafood", 100.0, 60.0, 8.0),
    "pozoleria": ("Pozolería", "seafood", 85.0, 45.0, 5.0),
    "tamaleria": ("Tamalería", "generic", 25.0, 12.0, 2.0),
    "eloteria": ("Elotería", "fruit_vegetables", 25.0, 10.0, 2.0),
    "relojeria": ("Relojería", "generic", 500.0, 250.0, 50.0),
    "joyeria": ("Joyería", "generic", 1500.0, 800.0, 200.0),
    "optica": ("Óptica", "generic", 800.0, 400.0, 100.0),
    "farmacia": ("Farmacia", "generic", 120.0, 70.0, 10.0),
    "veterinaria": ("Veterinaria", "generic", 300.0, 150.0, 30.0),
    "cerrajeria": ("Cerrajería", "generic", 150.0, 75.0, 15.0),
    "taller_mecanico": ("Taller Mecánico", "generic", 500.0, 250.0, 50.0),
    "taller_electrico": ("Taller Eléctrico", "generic", 400.0, 200.0, 40.0),
    "taller_de_bicis": ("Taller de Bicicletas", "generic", 250.0, 120.0, 20.0),
    "carpinteria": ("Carpintería", "generic", 600.0, 300.0, 50.0),
    "herreria": ("Herrería", "generic", 800.0, 450.0, 80.0),
    "plomeria": ("Plomería", "generic", 300.0, 150.0, 30.0),
    "vidrieria": ("Vidriería", "generic", 400.0, 200.0, 40.0),
    "muebleria": ("Mueblería", "generic", 2500.0, 1500.0, 300.0),
    "tapiceria": ("Tapicería", "generic", 600.0, 300.0, 50.0),
    "sastreria": ("Sastrería", "generic", 350.0, 170.0, 30.0),
    "lavanderia": ("Lavandería", "generic", 45.0, 20.0, 3.0),
    "tintoreria": ("Tintorería", "generic", 90.0, 45.0, 5.0),
    "estetica": ("Estética", "generic", 120.0, 50.0, 10.0),
    "barberia": ("Barbería", "generic", 100.0, 40.0, 8.0),
    "spa": ("Spa", "generic", 450.0, 180.0, 30.0),
    "gimnasio": ("Gimnasio", "generic", 30.0, 10.0, 2.0),
    "libreria": ("Librería", "generic", 180.0, 110.0, 20.0),
    "tienda_de_ropa": ("Tienda de Ropa", "generic", 280.0, 140.0, 20.0),
    "tienda_de_calzado": ("Tienda de Calzado", "generic", 400.0, 220.0, 45.0),
    "tienda_de_deportes": ("Tienda de Deportes", "generic", 350.0, 200.0, 40.0),
    "tienda_de_electronica": ("Tienda de Electrónica", "generic", 950.0, 600.0, 100.0),
    "tienda_de_celulares": ("Tienda de Celulares", "generic", 1800.0, 1200.0, 200.0),
    "tienda_de_computacion": ("Tienda de Computación", "generic", 2500.0, 1600.0, 300.0),
    "tienda_de_videojuegos": ("Tienda de Videojuegos", "generic", 800.0, 500.0, 80.0),
    "tienda_de_discos": ("Tienda de Música", "generic", 150.0, 90.0, 15.0),
    "tienda_de_artesanias": ("Tienda de Artesanías", "generic", 180.0, 90.0, 15.0),
    "tienda_de_antiguedades": ("Tienda de Antiguedades", "generic", 1200.0, 700.0, 100.0),
    "tienda_de_instrumentos": ("Tienda de Instrumentos", "generic", 1500.0, 900.0, 150.0),
    "tienda_de_pinturas": ("Tienda de Pinturas", "generic", 250.0, 150.0, 25.0),
    "tienda_de_telas": ("Tienda de Telas", "generic", 80.0, 40.0, 5.0),
    "tienda_de_plasticos": ("Tienda de Plásticos", "generic", 30.0, 15.0, 2.0),
    "tienda_de_desechables": ("Tienda de Desechables", "generic", 20.0, 10.0, 1.0),
    "tienda_de_limpieza": ("Tienda de Limpieza", "generic", 35.0, 18.0, 3.0),
    "tienda_de_materias_primas": ("Tienda de Materias Primas", "generic", 40.0, 22.0, 3.0),
    "tienda_de_semillas": ("Tienda de Semillas", "fruit_vegetables", 35.0, 18.0, 3.0),
    "tienda_de_especias": ("Tienda de Especias", "fruit_vegetables", 50.0, 25.0, 4.0),
    "tienda_de_chiles_secos": ("Tienda de Chiles Secos", "fruit_vegetables", 65.0, 35.0, 5.0),
    "tienda_de_frutos_secos": ("Tienda de Frutos Secos", "fruit_vegetables", 120.0, 65.0, 10.0),
    "tienda_de_pescado_seco": ("Tienda de Pescado Seco", "seafood", 150.0, 95.0, 15.0),
    "tienda_de_plantas_medicinales": ("Tienda de Plantas Medicinales", "flowers", 45.0, 20.0, 3.0),
    "tienda_de_veladoras": ("Tienda de Veladoras", "generic", 25.0, 12.0, 2.0),
    "tienda_de_articulos_religiosos": ("Tienda de Artículos Religiosos", "generic", 150.0, 80.0, 10.0),
    "tienda_de_disfraces": ("Tienda de Disfraces", "generic", 350.0, 180.0, 30.0),
    "tienda_de_maquillaje": ("Tienda de Maquillaje", "generic", 80.0, 40.0, 5.0),
    "tienda_de_plantas": ("Tienda de Plantas", "flowers", 65.0, 30.0, 5.0),
    "tienda_de_macetas": ("Tienda de Macetas", "generic", 120.0, 60.0, 10.0),
    "tienda_de_regalos": ("Tienda de Regalos", "generic", 150.0, 80.0, 10.0),
    "tienda_de_cosmeticos": ("Tienda de Cosméticos", "generic", 75.0, 38.0, 5.0)
}

adjectives = {
    "del_barrio": " del Barrio",
    "de_la_esquina": " de la Esquina",
    "express": " Express",
    "premium": " Premium",
    "tradicional": " Tradicional",
    "familiar": " Familiar",
    "popular": " Popular",
    "economica": " Económica",
    "del_centro": " del Centro",
    "gourmet": " Gourmet"
}

INVENTORY_PARAMETERS = {}

for g_key, g_val in giros.items():
    name, parent_cat, base_price, base_cost, base_salvage = g_val
    for a_key, a_val in adjectives.items():
        cat_key = f"{g_key}_{a_key}"
        params = dict(BASE_PARAMS[parent_cat])
        price = base_price
        cost = base_cost
        
        if a_key in ["gourmet", "premium"]:
            price *= 1.5
            cost *= 1.3
        elif a_key == "economica":
            price *= 0.7
            cost *= 0.7
            
        params["default_price"] = round(price, 2)
        params["default_cost"] = round(cost, 2)
        params["default_salvage"] = round(base_salvage, 2)
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
    
    for g_key, g_val in giros.items():
        if category_key.startswith(g_key + "_"):
            return g_val[0]
                
    return category_key.replace("_", " ").title()

def get_category_group(category_key: str) -> str:
    """Retorna el grupo termodinámico (seafood, flowers, etc.) de la categoría."""
    if category_key in BASE_PARAMS:
        return category_key
    for g_key, g_val in giros.items():
        if category_key.startswith(g_key + "_"):
            return g_val[1]
    return "generic"

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
