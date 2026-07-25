# -*- coding: utf-8 -*-
"""Puertos abstractos (interfaces) de la arquitectura hexagonal de Merma Cero."""
from abc import ABC, abstractmethod
from typing import Optional
from merma_cero.domain.entities import Vendor, WeatherState

from typing import Optional, List

class VendorRepositoryPort(ABC):
    """Puerto para persistencia y lectura de datos de comerciantes y límites."""

    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[Vendor]:
        """Recupera un vendedor por su identificador único de teléfono."""
        pass

    @abstractmethod
    def save(self, vendor: Vendor) -> None:
        """Persiste un vendedor en el repositorio."""
        pass

    @abstractmethod
    def get_all(self) -> List[Vendor]:
        """Recupera la lista completa de todos los vendedores registrados."""
        pass

class WeatherPort(ABC):
    """Puerto para la obtención de pronósticos climáticos georreferenciados."""

    @abstractmethod
    def get_weather(self, lat: float, lon: float) -> WeatherState:
        """Retorna el estado de clima actual o estimado para coordenadas dadas."""
        pass

class MessagePort(ABC):
    """Puerto de salida para canalizar notificaciones/respuestas al vendedor."""

    @abstractmethod
    def send_message(self, phone: str, text: str) -> bool:
        """Envía una respuesta conversacional asíncrona de baja latencia al vendedor."""
        pass

class AIServicePort(ABC):
    """Puerto para generar recomendaciones personalizadas utilizando inteligencia artificial."""

    @abstractmethod
    def get_recommendation(
        self,
        category: str,
        weather: WeatherState,
        shelf_life: float,
        optimal_purchase_pct: float
    ) -> str:
        """Genera recomendaciones personalizadas adaptadas al negocio usando IA."""
        pass

