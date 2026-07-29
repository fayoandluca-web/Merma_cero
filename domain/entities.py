# -*- coding: utf-8 -*-
"""Entidades de dominio validadas bajo el estándar de ciberseguridad Pydantic."""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import re
from merma_cero.config import (
    INVENTORY_PARAMETERS,
    MAX_TEMP_CLIPPING,
    MIN_TEMP_CLIPPING,
    MAX_HUMIDITY_CLIPPING,
    MIN_HUMIDITY_CLIPPING,
)
from merma_cero.domain.exceptions import InvalidInputError

class WeatherState(BaseModel):
    """Representa el estado climático actual y pronosticado para un punto geográfico."""
    temperature: float = Field(..., description="Temperatura ambiente en grados Celsius")
    relative_humidity: float = Field(..., description="Humedad relativa en fracción [0.0, 1.0]")
    precipitation_probability: float = Field(..., description="Probabilidad de lluvia en fracción [0.0, 1.0]")

    @field_validator("temperature")
    @classmethod
    def validate_and_clip_temp(cls, v: float) -> float:
        """Aplica clipping físico de seguridad (Murphy Law) para evitar desbordamientos."""
        if v > MAX_TEMP_CLIPPING:
            return MAX_TEMP_CLIPPING
        if v < MIN_TEMP_CLIPPING:
            return MIN_TEMP_CLIPPING
        return v

    @field_validator("relative_humidity", "precipitation_probability")
    @classmethod
    def validate_and_clip_probabilities(cls, v: float) -> float:
        """Asegura límites estocásticos para evitar errores algebraicos en solvers."""
        if v > MAX_HUMIDITY_CLIPPING:
            return MAX_HUMIDITY_CLIPPING
        if v < MIN_HUMIDITY_CLIPPING:
            return MIN_HUMIDITY_CLIPPING
        return v

class Vendor(BaseModel):
    """Vendedor registrado de la economía informal."""
    phone: str = Field(..., description="Identificador único E.164 (número telefónico para WhatsApp)")
    latitude: float = Field(..., description="Latitud de operación comercial")
    longitude: float = Field(..., description="Longitud de operación comercial")
    inventory_category: str = Field(..., description="Categoría de producto vendido")
    registration_timestamp: float = Field(..., description="Timestamp Unix de registro")
    rate_limit_tokens: float = Field(10.0, description="Tokens de rate limiting actuales")
    rate_limit_last_update: float = Field(..., description="Última actualización de tokens de rate limiting")
    message_history: List[dict] = Field(default_factory=list, description="Historial de mensajes y recomendaciones de la IA")
    opt_in: bool = Field(False, description="Consentimiento explícito de opt-in de WhatsApp")
    name: str = Field("Comerciante Anónimo", description="Nombre del comerciante o de su negocio")



    @field_validator("phone")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        """Sanitiza el identificador (teléfono o ID de Telegram) para prevenir inyecciones (Zero Trust)."""
        pattern_e164 = r"^\+?[1-9]\d{1,14}$"  # Estándar E.164
        pattern_telegram = r"^telegram:\d+$"  # Formato Telegram
        if not (re.match(pattern_e164, v) or re.match(pattern_telegram, v)):
            raise InvalidInputError("Formato de identificador inválido (requiere E.164 o telegram:chat_id).")
        return v

    @field_validator("inventory_category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Garantiza la existencia de la categoría para cálculos cinéticos de descomposición."""
        valid_cats = list(INVENTORY_PARAMETERS.keys())
        if v not in valid_cats:
            raise InvalidInputError(f"Categoría de inventario '{v}' no soportada. Válidas: {valid_cats}")
        return v

    @model_validator(mode="after")
    def validate_geographic_coordinates(self) -> "Vendor":
        """Valida que las coordenadas geográficas caigan en límites de la corteza terrestre."""
        if not (-90.0 <= self.latitude <= 90.0):
            raise InvalidInputError("Latitud fuera de límites terrestres [-90, 90].")
        if not (-180.0 <= self.longitude <= 180.0):
            raise InvalidInputError("Longitud fuera de límites terrestres [-180, 180].")
        return self
