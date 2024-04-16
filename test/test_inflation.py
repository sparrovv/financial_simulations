from decimal import Decimal
from finsim.inflation import random_inflation_gen, inflation_from_file_gen
import tempfile


def test_random_inflation_gen() -> None:
    g = random_inflation_gen(range=(1, 5))
    assert next(g) >= Decimal("0.01") and next(g) <= Decimal("0.05")
    assert next(g) >= Decimal("0.01")
    assert next(g) >= Decimal("0.01")


def test_from_file_gen() -> None:
    inflation_date = """date,value
    2020,0.024
    2021,0.08
    2022,0.14
"""

    file_path = None

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp.write(inflation_date)
        file_path = temp.name

    gen = inflation_from_file_gen(file_path)

    for _ in range(12):
        assert next(gen) == Decimal("0.002")

    for _ in range(12):
        assert next(gen) == Decimal("0.007")

    for _ in range(30):
        # that it doesn't fail
        assert next(gen)
