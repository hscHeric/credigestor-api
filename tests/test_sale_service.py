import pytest
from datetime import date
from decimal import Decimal
from app.services.sale_service import _last_day_of_month, add_months, _split_amount

# --- Testes de Data ---

def test_last_day_february_leap_year():
    """Testa se Fevereiro tem 29 dias em ano bissexto (2024)"""
    assert _last_day_of_month(2024, 2) == 29

def test_last_day_february_non_leap_year():
    """Testa se Fevereiro tem 28 dias em ano normal (2023)"""
    assert _last_day_of_month(2023, 2) == 28

def test_last_day_30_days_months():
    """Testa meses com 30 dias (Abril)"""
    assert _last_day_of_month(2023, 4) == 30

def test_add_months_same_day():
    """Testa adicionar 1 mês (10/01 -> 10/02)"""
    d = date(2023, 1, 10)
    new_date = add_months(d, 1)
    assert new_date == date(2023, 2, 10)

def test_add_months_end_of_month_adjustment():
    """Testa o ajuste de dia (31/01 + 1 mês -> 28/02)"""
    d = date(2023, 1, 31)
    new_date = add_months(d, 1)
    assert new_date == date(2023, 2, 28)

# --- Testes de Dinheiro (Divisão de Parcelas) ---

def test_split_amount_exact_division():
    """Testa divisão exata (100 / 2 = 50, 50)"""
    total = Decimal("100.00")
    parts = _split_amount(total, 2)
    assert parts == [Decimal("50.00"), Decimal("50.00")]
    assert sum(parts) == total

def test_split_amount_with_remainder():
    """Testa dízima periódica (100 / 3 = 33.33, 33.33, 33.34)"""
    total = Decimal("100.00")
    parts = _split_amount(total, 3)
    
    # Verifica se gerou 3 parcelas
    assert len(parts) == 3
    # A soma TEM que bater 100.00
    assert sum(parts) == total
    # A diferença de centavos fica na última
    assert parts[0] == Decimal("33.33")
    assert parts[-1] == Decimal("33.34")