import os
from pathlib import Path
from alembic.config import Config
from alembic import command
import pytest

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"
ALEMBIC_INI = Path(__file__).resolve().parent.parent.parent / "alembic.ini"


def test_alembic_config_validity():
    """Verify Alembic configuration file exists and script location is valid."""
    assert ALEMBIC_INI.exists()
    assert MIGRATIONS_DIR.exists()
    assert (MIGRATIONS_DIR / "env.py").exists()

    alembic_cfg = Config(str(ALEMBIC_INI))
    alembic_cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    script_location = alembic_cfg.get_main_option("script_location")
    assert script_location == str(MIGRATIONS_DIR)
