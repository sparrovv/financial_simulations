from decimal import Decimal


def calculate_monthly_payment(
    principal: Decimal,
    rate: Decimal,
    number_of_months_left: int,
    payments_per_year: int = 12,
) -> tuple[Decimal, Decimal]:
    calculated_rate = rate / Decimal(100) / payments_per_year

    numerator = calculated_rate * (
        (calculated_rate + Decimal(1)) ** number_of_months_left
    )
    denominator = ((Decimal(1) + calculated_rate) ** number_of_months_left) - Decimal(1)
    monthly_payment = principal * (numerator / denominator)

    # round to 2 decimal places
    return round(monthly_payment, 2), _calculate_monthly_interest(
        principal, rate, payments_per_year
    )


def _calculate_monthly_interest(
    principal: Decimal,
    rate: Decimal,
    payments_per_year: int = 12,
) -> Decimal:
    calculated_rate = rate / Decimal(100) / payments_per_year

    monthly_interest = principal * calculated_rate

    # round to 2 decimal places
    return round(monthly_interest, 2)
