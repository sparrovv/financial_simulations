from decimal import Decimal

from .mortgage import calculate_monthly_payment


def test_mortgage() -> None:

    monthly, interest = calculate_monthly_payment(
        principal=Decimal("154275"),
        rate=Decimal("7.88"),
        number_of_months_left=94,
    )

    assert monthly, interest == (Decimal("2204.76"), Decimal("1016.88"))
