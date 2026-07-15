"""
Schema initialization and seed data for first run.

Creates tables and inserts default categories / units so Product forms
have reference data immediately after USB copy.
"""

from __future__ import annotations

from sqlalchemy import select

from config.settings import DEFAULT_CATEGORIES, DEFAULT_UNITS
from database.connection import create_all_tables, session_scope
from models.entities import Category, Unit
from utils.logger import get_logger

logger = get_logger("schema")


def seed_reference_data() -> None:
    """Insert default categories and units when the tables are empty."""
    with session_scope() as session:
        existing_units = session.scalar(select(Unit.id).limit(1))
        if existing_units is None:
            for name in DEFAULT_UNITS:
                session.add(Unit(name=name, abbreviation=name[:3].upper()))
            logger.info("Seeded %d default units", len(DEFAULT_UNITS))

        existing_categories = session.scalar(select(Category.id).limit(1))
        if existing_categories is None:
            for name in DEFAULT_CATEGORIES:
                session.add(Category(name=name))
            logger.info("Seeded %d default categories", len(DEFAULT_CATEGORIES))


def initialize_database() -> None:
    """Full first-run (or every-run) database bootstrap."""
    create_all_tables()
    seed_reference_data()
    logger.info("Database initialization complete")
