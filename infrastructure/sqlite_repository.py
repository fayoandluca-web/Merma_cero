# -*- coding: utf-8 -*-
"""Repositorio SQLite robustecido para persistencia transaccional y de alta concurrencia."""
import os
import sqlite3
import json
import threading
from typing import Optional, List
from merma_cero.config import BASE_DIR
from merma_cero.domain.entities import Vendor
from merma_cero.application.ports import VendorRepositoryPort

class SQLiteVendorRepository(VendorRepositoryPort):
    """Adaptador de persistencia SQLite transaccional y de alto rendimiento."""

    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            # Por defecto usamos un archivo merma_cero.db en el directorio del proyecto
            self.db_path = os.path.join(BASE_DIR, "merma_cero.db")
        else:
            self.db_path = db_path
        
        self.lock = threading.Lock()
        self._initialize_db()

    def _get_connection(self):
        """Retorna una conexión activa a SQLite configurando timeout para escrituras concurrentes."""
        return sqlite3.connect(self.db_path, timeout=15.0)

    def _initialize_db(self) -> None:
        """Crea el esquema de base de datos si no existe."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vendors (
                        phone TEXT PRIMARY KEY,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        inventory_category TEXT NOT NULL,
                        registration_timestamp REAL NOT NULL,
                        rate_limit_tokens REAL NOT NULL,
                        rate_limit_last_update REAL NOT NULL,
                        message_history TEXT NOT NULL
                    )
                """)
                # Migración automática de columna para compatibilidad retrospectiva
                try:
                    cursor.execute("ALTER TABLE vendors ADD COLUMN opt_in INTEGER DEFAULT 0")
                except sqlite3.OperationalError:
                    # La columna ya existe, omitir
                    pass
                try:
                    cursor.execute("ALTER TABLE vendors ADD COLUMN name TEXT DEFAULT 'Comerciante Anónimo'")
                except sqlite3.OperationalError:
                    # La columna ya existe, omitir
                    pass
                try:
                    cursor.execute("ALTER TABLE vendors ADD COLUMN address TEXT DEFAULT 'Colima, México'")
                except sqlite3.OperationalError:
                    # La columna ya existe, omitir
                    pass
                try:
                    cursor.execute("ALTER TABLE vendors ADD COLUMN is_simulated INTEGER DEFAULT 0")
                except sqlite3.OperationalError:
                    # La columna ya existe, omitir
                    pass
                conn.commit()
            finally:
                conn.close()

    def get_by_phone(self, phone: str) -> Optional[Vendor]:
        """Recupera un vendedor leyendo de forma segura de SQLite."""
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT phone, latitude, longitude, inventory_category, 
                           registration_timestamp, rate_limit_tokens, 
                           rate_limit_last_update, message_history, opt_in, name, address, is_simulated 
                    FROM vendors WHERE phone = ?
                """, (phone,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Deserializar el historial de mensajes
                history = json.loads(row[7])
                
                # Manejar compatibilidad si opt_in/name/address/is_simulated no están en la base de datos (por si acaso)
                opt_in_val = bool(row[8]) if len(row) > 8 else False
                name_val = row[9] if len(row) > 9 else "Comerciante Anónimo"
                address_val = row[10] if len(row) > 10 else "Colima, México"
                is_simulated_val = bool(row[11]) if len(row) > 11 else False
                
                return Vendor(
                    phone=row[0],
                    latitude=row[1],
                    longitude=row[2],
                    inventory_category=row[3],
                    registration_timestamp=row[4],
                    rate_limit_tokens=row[5],
                    rate_limit_last_update=row[6],
                    message_history=history,
                    opt_in=opt_in_val,
                    name=name_val,
                    address=address_val,
                    is_simulated=is_simulated_val
                )
            except Exception:
                # En caso de fallo (ej. base de datos vacía o corrupta), retornamos None para auto-recuperación
                return None
            finally:
                conn.close()

    def save(self, vendor: Vendor) -> None:
        """Persiste o actualiza al vendedor aplicando transaccionalidad atómica (UPSERT)."""
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                history_json = json.dumps(vendor.message_history, ensure_ascii=False)
                
                cursor.execute("""
                    INSERT INTO vendors (
                        phone, latitude, longitude, inventory_category, 
                        registration_timestamp, rate_limit_tokens, 
                        rate_limit_last_update, message_history, opt_in, name, address, is_simulated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(phone) DO UPDATE SET
                        latitude=excluded.latitude,
                        longitude=excluded.longitude,
                        inventory_category=excluded.inventory_category,
                        rate_limit_tokens=excluded.rate_limit_tokens,
                        rate_limit_last_update=excluded.rate_limit_last_update,
                        message_history=excluded.message_history,
                        opt_in=excluded.opt_in,
                        name=excluded.name,
                        address=excluded.address,
                        is_simulated=excluded.is_simulated
                """, (
                    vendor.phone,
                    vendor.latitude,
                    vendor.longitude,
                    vendor.inventory_category,
                    vendor.registration_timestamp,
                    vendor.rate_limit_tokens,
                    vendor.rate_limit_last_update,
                    history_json,
                    1 if vendor.opt_in else 0,
                    vendor.name,
                    vendor.address,
                    1 if vendor.is_simulated else 0
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise IOError(f"Fallo en transacción SQLite de guardado: {e}")
            finally:
                conn.close()

    def get_all(self) -> List[Vendor]:
        """Recupera la lista completa de todos los vendedores registrados."""
        with self.lock:
            conn = self._get_connection()
            vendors = []
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT phone, latitude, longitude, inventory_category, 
                           registration_timestamp, rate_limit_tokens, 
                           rate_limit_last_update, message_history, opt_in, name, address, is_simulated 
                    FROM vendors
                """)
                rows = cursor.fetchall()
                for row in rows:
                    history = json.loads(row[7])
                    opt_in_val = bool(row[8]) if len(row) > 8 else False
                    name_val = row[9] if len(row) > 9 else "Comerciante Anónimo"
                    address_val = row[10] if len(row) > 10 else "Colima, México"
                    is_simulated_val = bool(row[11]) if len(row) > 11 else False
                    vendors.append(Vendor(
                        phone=row[0],
                        latitude=row[1],
                        longitude=row[2],
                        inventory_category=row[3],
                        registration_timestamp=row[4],
                        rate_limit_tokens=row[5],
                        rate_limit_last_update=row[6],
                        message_history=history,
                        opt_in=opt_in_val,
                        name=name_val,
                        address=address_val,
                        is_simulated=is_simulated_val
                    ))
            finally:
                conn.close()
            return vendors
