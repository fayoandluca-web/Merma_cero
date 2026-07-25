# -*- coding: utf-8 -*-
"""Módulo de alias motor.py para cumplimiento estricto del estándar x200.

Redirige la lógica del motor matemático al modelo de dominio.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Exponer clases del motor del dominio directamente
from merma_cero.domain.models import (
    DecayKinetics,
    GARCHVolatilityModel,
    KellyMermaSizer,
    MonteCarloMermaSimulator
)
