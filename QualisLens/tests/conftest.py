"""Configuração e fixtures compartilhadas dos testes QualisLens."""

import sys
from pathlib import Path

# Permite importar os módulos de qualislens/ sem instalar como pacote
QUALISLENS_DIR = Path(__file__).parent.parent / "qualislens"
sys.path.insert(0, str(QUALISLENS_DIR))

import pytest
from qualis_db import QualisDB

BASE_DIR = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def db() -> QualisDB:
    """Instância QualisDB compartilhada por toda a sessão de testes."""
    return QualisDB(
        path_2017=str(BASE_DIR / "base" / "qualis_2017_2020.csv"),
        path_2025=str(BASE_DIR / "base" / "qualis_2021_2024.csv"),
    )


@pytest.fixture(scope="session")
def test_dir() -> Path:
    return BASE_DIR / "test"
