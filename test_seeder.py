# -*- coding: utf-8 -*-
"""Suite de pruebas unitarias para el módulo de siembra (seeder.py)."""

import os
import sqlite3
import unittest
import time
import json
from unittest.mock import Mock, patch

from merma_cero.domain.entities import Vendor
from merma_cero.infrastructure.sqlite_repository import SQLiteVendorRepository
from merma_cero.infrastructure.seeder import seed_database
from merma_cero.application.ports import VendorRepositoryPort


class FakeVendorRepository(VendorRepositoryPort):
    """Fake repository to test the seeder fallback logic."""
    def __init__(self):
        self.vendors = {}

    def get_by_phone(self, phone: str):
        return self.vendors.get(phone)

    def save(self, vendor: Vendor) -> None:
        self.vendors[vendor.phone] = vendor

    def get_all(self):
        return list(self.vendors.values())


class TestSeederSystem(unittest.TestCase):

    def setUp(self) -> None:
        """Inicialización de la base de datos de pruebas."""
        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_seeder_database.db")
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass
        self.repo = SQLiteVendorRepository(db_path=self.test_db_path)

    def tearDown(self) -> None:
        """Limpieza de base de datos de pruebas."""
        try:
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
        except Exception:
            pass

    # =========================================================================
    # 1. HAPPY PATH (Casos de Éxito)
    # =========================================================================

    def test_seeding_generates_exact_1000_vendors(self) -> None:
        """Verifica que el seeder inserte exactamente 1000 vendedores realistas en la base de datos vacía."""
        # Se siembra la DB
        seed_database(self.repo)

        # Se recuperan todos los registros
        vendors = self.repo.get_all()
        self.assertEqual(len(vendors), 1000)

        # Validaciones de consistencia de los datos insertados
        categories_set = {"seafood", "flowers", "fruit_vegetables", "dairy", "generic"}
        
        # Límites geográficos amplios que cubren CDMX, Colima, Guadalajara y Monterrey
        # Latitudes de México: ~15 a ~33. Longitudes de México: ~-118 a ~-90.
        min_lat, max_lat = 18.0, 27.0
        min_lon, max_lon = -105.0, -98.0

        for vendor in vendors:
            # 1. Validación de número telefónico
            self.assertTrue(vendor.phone.startswith("+52"))
            self.assertEqual(len(vendor.phone), 13)  # +52 + 10 dígitos = 13
            self.assertTrue(vendor.phone[3:].isdigit())

            # 2. Validación de categoría de inventario
            self.assertIn(vendor.inventory_category, categories_set)

            # 3. Validación de coordenadas dentro de los rangos de mercados seleccionados
            self.assertTrue(min_lat <= vendor.latitude <= max_lat, f"Latitud fuera de límites: {vendor.latitude}")
            self.assertTrue(min_lon <= vendor.longitude <= max_lon, f"Longitud fuera de límites: {vendor.longitude}")

            # 4. Consentimiento activo (opt-in)
            self.assertTrue(vendor.opt_in)

            # 5. Validación del historial de mensajes (entre 2 y 5 interacciones)
            self.assertTrue(2 <= len(vendor.message_history) <= 5)

            for entry in vendor.message_history:
                self.assertEqual(entry["type"], "inbound_request")
                self.assertIsNotNone(entry["text_received"])
                self.assertIsNotNone(entry["message_sent"])
                self.assertIn("weather", entry)
                self.assertIn("metrics", entry)
                
                # Validar la presencia del costo ahorrado estimado
                self.assertIn("saved_cost_estimated", entry["metrics"])
                self.assertIsInstance(entry["metrics"]["saved_cost_estimated"], float)
                self.assertTrue(entry["metrics"]["saved_cost_estimated"] >= 0.0)

                # Validar que prediction_accurate sea booleano o None
                self.assertIn(entry["prediction_accurate"], [True, False, None])

    # =========================================================================
    # 2. EDGE CASES (Casos Límite y Extremos)
    # =========================================================================

    def test_seeder_does_not_overwrite_if_already_populated(self) -> None:
        """Verifica que si la base de datos ya contiene al menos un registro, el seeder no haga nada."""
        # Insertar un vendedor dummy para que no esté vacía
        dummy_vendor = Vendor(
            phone="+525500000000",
            latitude=19.43,
            longitude=-99.13,
            inventory_category="generic",
            registration_timestamp=time.time(),
            rate_limit_last_update=time.time(),
            opt_in=True
        )
        self.repo.save(dummy_vendor)

        # Intentar ejecutar el seeder
        seed_database(self.repo)

        # Verificar que solo exista el vendedor dummy original
        vendors = self.repo.get_all()
        self.assertEqual(len(vendors), 1)
        self.assertEqual(vendors[0].phone, "+525500000000")

    def test_seeder_fallback_path(self) -> None:
        """Verifica que el seeder funcione con un repositorio que no sea SQLiteVendorRepository usando el fallback."""
        fake_repo = FakeVendorRepository()
        
        # Ejecutar siembra
        seed_database(fake_repo)
        
        # Debe haber guardado exactamente 1000 registros
        vendors = fake_repo.get_all()
        self.assertEqual(len(vendors), 1000)
        self.assertTrue(vendors[0].opt_in)

    # =========================================================================
    # 3. PROVOKED FAILURES (Fallos Provocados)
    # =========================================================================

    def test_seeder_handles_database_error_and_rolls_back(self) -> None:
        """Verifica que el seeder aborte y levante IOError si ocurre un error inesperado al escribir en SQLite."""
        # Forzar un error en executemany mockeando el cursor retornado por _get_connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.executemany.side_effect = sqlite3.OperationalError("Simulated database failure")
        mock_conn.cursor.return_value = mock_cursor
        
        with patch.object(self.repo, "_get_connection", return_value=mock_conn):
            with self.assertRaises(IOError):
                seed_database(self.repo)

        # Verificar que la base de datos continúe vacía (se hizo rollback)
        vendors = self.repo.get_all()
        self.assertEqual(len(vendors), 0)


if __name__ == "__main__":
    unittest.main()
