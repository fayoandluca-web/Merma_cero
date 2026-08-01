# -*- coding: utf-8 -*-
"""Repositorio SQLAlchemy para persistencia transaccional y de alta concurrencia (PostgreSQL/SQLite)."""
import os
import json
import threading
from typing import Optional, List

from sqlalchemy import create_engine, Column, String, Float, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, SingletonThreadPool
from sqlalchemy.exc import SQLAlchemyError

from merma_cero.config import BASE_DIR, DATABASE_URL
from merma_cero.domain.entities import Vendor
from merma_cero.application.ports import VendorRepositoryPort

Base = declarative_base()

class VendorModel(Base):
    """Modelo de base de datos SQLAlchemy para los vendedores."""
    __tablename__ = 'vendors'

    phone = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    inventory_category = Column(String, nullable=False)
    registration_timestamp = Column(Float, nullable=False)
    rate_limit_tokens = Column(Float, nullable=False)
    rate_limit_last_update = Column(Float, nullable=False)
    message_history = Column(String, nullable=False)  # JSON string
    opt_in = Column(Boolean, default=False)
    name = Column(String, default='Comerciante Anónimo')
    address = Column(String, default='Colima, México')
    is_simulated = Column(Boolean, default=False)
    age = Column(Integer, nullable=True)
    business_years = Column(Float, nullable=True)

class SQLiteVendorRepository(VendorRepositoryPort):
    """Adaptador de persistencia usando SQLAlchemy (soporta PostgreSQL y SQLite híbrido)."""

    def __init__(self, db_path: Optional[str] = None):
        if DATABASE_URL and (not db_path or "test_" not in db_path):
            # PostgreSQL si DATABASE_URL está presente y no se sobreescribe con db_path
            engine_url = DATABASE_URL
            if engine_url.startswith("postgres://"):
                engine_url = engine_url.replace("postgres://", "postgresql://", 1)
            self.engine = create_engine(engine_url, poolclass=QueuePool, pool_size=5, max_overflow=10)
        else:
            # Híbrido: SQLite local
            if not db_path:
                db_path = os.path.join(BASE_DIR, "merma_cero.db")
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, poolclass=SingletonThreadPool)

        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.lock = threading.Lock()

    def close(self) -> None:
        """Cierra el pool de conexiones y libera el archivo de base de datos."""
        self.engine.dispose()

    def _get_connection(self):
        """Devuelve una conexión cruda para compatibilidad con el seeder y scripts legacy."""
        return self.engine.raw_connection()

    def _to_entity(self, model: VendorModel) -> Vendor:
        try:
            history = json.loads(model.message_history)
        except Exception:
            history = []
            
        return Vendor(
            phone=model.phone,
            latitude=model.latitude,
            longitude=model.longitude,
            inventory_category=model.inventory_category,
            registration_timestamp=model.registration_timestamp,
            rate_limit_tokens=model.rate_limit_tokens,
            rate_limit_last_update=model.rate_limit_last_update,
            message_history=history,
            opt_in=bool(model.opt_in),
            name=model.name,
            address=model.address,
            is_simulated=bool(model.is_simulated),
            age=model.age,
            business_years=model.business_years
        )

    def get_by_phone(self, phone: str) -> Optional[Vendor]:
        """Recupera un vendedor leyendo de forma segura a través de SQLAlchemy."""
        with self.lock:
            with self.SessionLocal() as session:
                try:
                    model = session.query(VendorModel).filter(VendorModel.phone == phone).first()
                    if model:
                        return self._to_entity(model)
                    return None
                except Exception:
                    return None

    def save(self, vendor: Vendor) -> None:
        """Persiste o actualiza al vendedor aplicando transaccionalidad atómica."""
        with self.lock:
            with self.SessionLocal() as session:
                try:
                    history_json = json.dumps(vendor.message_history, ensure_ascii=False)
                    model = session.query(VendorModel).filter(VendorModel.phone == vendor.phone).first()
                    
                    if not model:
                        model = VendorModel(phone=vendor.phone)
                        session.add(model)
                        
                    model.latitude = vendor.latitude
                    model.longitude = vendor.longitude
                    model.inventory_category = vendor.inventory_category
                    model.registration_timestamp = vendor.registration_timestamp
                    model.rate_limit_tokens = vendor.rate_limit_tokens
                    model.rate_limit_last_update = vendor.rate_limit_last_update
                    model.message_history = history_json
                    model.opt_in = vendor.opt_in
                    model.name = vendor.name
                    model.address = vendor.address
                    model.is_simulated = vendor.is_simulated
                    model.age = vendor.age
                    model.business_years = vendor.business_years
                    
                    session.commit()
                except SQLAlchemyError as e:
                    session.rollback()
                    raise IOError(f"Fallo en transacción de guardado: {e}")

    def get_all(self) -> List[Vendor]:
        """Recupera la lista completa de todos los vendedores registrados."""
        with self.lock:
            with self.SessionLocal() as session:
                try:
                    models = session.query(VendorModel).all()
                    return [self._to_entity(m) for m in models]
                except Exception:
                    return []
