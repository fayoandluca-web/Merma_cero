# -*- coding: utf-8 -*-
"""Excepciones de dominio y negocio para el Proyecto Merma Cero."""

class DomainError(Exception):
    """Excepción base para todos los errores de dominio de Merma Cero."""
    pass

class VendorNotFoundError(DomainError):
    """Lanzada cuando un vendedor no existe en la persistencia."""
    pass

class InvalidInputError(DomainError):
    """Lanzada cuando se ingresan datos que violan los límites del sistema o de tipado."""
    pass

class WeatherFetchError(DomainError):
    """Lanzada cuando colapsa el servicio climatológico activo y los fallbacks."""
    pass

class SecurityViolationError(DomainError):
    """Lanzada ante violaciones de cuotas de rate limiting o accesos no autorizados."""
    pass

class NumericalInstabilityError(DomainError):
    """Lanzada cuando un algoritmo numérico diverge o calcula valores no físicos."""
    pass
