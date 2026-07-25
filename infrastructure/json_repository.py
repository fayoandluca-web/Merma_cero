# -*- coding: utf-8 -*-
"""Repositorio JSON robustecido con control transaccional por Mutex y escritura atómica (Murphy Law)."""
import os
import json
import threading
from typing import Optional, Dict, List
from merma_cero.config import DATABASE_PATH
from merma_cero.domain.entities import Vendor
from merma_cero.application.ports import VendorRepositoryPort

class JSONVendorRepository(VendorRepositoryPort):
    """Adaptador de persistencia JSON transaccional."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._initialize_db_if_missing()

    def _initialize_db_if_missing(self) -> None:
        """Inicializa una base de datos JSON vacía pero estructurada de manera segura."""
        with self.lock:
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            if not os.path.exists(self.db_path):
                self._write_db_atomic({"vendors": {}})

    def get_by_phone(self, phone: str) -> Optional[Vendor]:
        """Recupera un vendedor leyendo de forma segura de la base de datos."""
        with self.lock:
            data = self._read_db()
            vendor_data = data.get("vendors", {}).get(phone)
            if not vendor_data:
                return None
            return Vendor(**vendor_data)

    def save(self, vendor: Vendor) -> None:
        """Persiste o actualiza al vendedor aplicando escritura atómica en disco."""
        with self.lock:
            data = self._read_db()
            if "vendors" not in data:
                data["vendors"] = {}
            data["vendors"][vendor.phone] = vendor.model_dump()
            self._write_db_atomic(data)

    def get_all(self) -> List[Vendor]:
        """Recupera la lista completa de todos los vendedores registrados."""
        with self.lock:
            data = self._read_db()
            vendors_dict = data.get("vendors", {})
            return [Vendor(**v) for v in vendors_dict.values()]


    def _read_db(self) -> Dict:
        """Lee el contenido actual de la base de datos."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Si el archivo está corrupto (Murphy), devolvemos estructura limpia para auto-recuperación
            return {"vendors": {}}

    def _write_db_atomic(self, data: Dict) -> None:
        """Escribe en la base de datos de manera atómica en dos etapas.
        
        Mitigación:
            1. Escribe en un archivo temporal (.tmp).
            2. Valida que el archivo temporal contenga un JSON estructurado correcto.
            3. Reemplaza atómicamente el archivo final usando operaciones del OS.
        """
        temp_path = f"{self.db_path}.tmp"
        
        # Etapa 1: Escritura en archivo temporal
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Etapa 2: Validación de la estructura escrita (Anti-corrupción)
        try:
            with open(temp_path, "r", encoding="utf-8") as f:
                json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # Eliminar temporal corrupto y abortar transacción
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"Fallo crítico en consistencia de escritura: {e}")

        # Etapa 3: Remplazo atómico
        if os.path.exists(self.db_path):
            os.replace(temp_path, self.db_path)
        else:
            os.rename(temp_path, self.db_path)
