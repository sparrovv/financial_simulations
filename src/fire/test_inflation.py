from decimal import Decimal
from .inflation import random_inflation_gen


def test_random_inflation_gen() -> None:
    g = random_inflation_gen(range=(1, 5))
    assert next(g) >= Decimal("0.01") and next(g) <= Decimal("0.05")
    assert next(g) >= Decimal("0.01")
    assert next(g) >= Decimal("0.01")
