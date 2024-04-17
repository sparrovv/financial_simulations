from datetime import date
from finsim.mortgage import calculate_monthly_payment


from dataclasses import asdict, dataclass, replace
from decimal import Decimal


@dataclass
class InvestmentProperty:
    market_value: Decimal
    monthly_income: Decimal
    mortgage_left: Decimal
    mortgage_rate: Decimal
    mortgage_months: int
    monthly_interest: Decimal = Decimal("0")
    monthly_payment: Decimal = Decimal("0")
    annual_rent_increase_rate: Decimal = Decimal("0")

    def is_with_mortgage(self) -> bool:
        return (
            self.mortgage_left > 0
            and self.mortgage_months > 0
            and self.mortgage_rate > 0
        )

    def net_cash_value(self) -> Decimal:
        return self.market_value - self.mortgage_left

    def to_dict(self):
        return asdict(self) | {"net_cash_value": self.net_cash_value()}

    def __post_init__(self):
        if self.is_with_mortgage():
            monthly_payment, monthly_interest = calculate_monthly_payment(
                principal=self.mortgage_left,
                rate=self.mortgage_rate,
                number_of_months_left=self.mortgage_months,
            )

            self.monthly_interest = monthly_interest
            self.monthly_payment = monthly_payment


def simulate_next_property_month(
    prev: InvestmentProperty, annual_property_appreciation_rate: Decimal, sim_date: date
) -> InvestmentProperty:
    new_market_value = round(
        prev.market_value
        + (prev.market_value * annual_property_appreciation_rate / Decimal("12")),
        2,
    )

    new_monthly_income = prev.monthly_income
    if sim_date.month == 1:
        new_monthly_income = prev.monthly_income * (1 + prev.annual_rent_increase_rate)

    if prev.is_with_mortgage() is False:
        return replace(prev, market_value=new_market_value)

    # calculate the principal
    monthly_principal = prev.monthly_payment - prev.monthly_interest

    new_mortgage_left = prev.mortgage_left - monthly_principal
    new_mortgage_months = prev.mortgage_months - 1

    return InvestmentProperty(
        market_value=new_market_value,
        monthly_income=new_monthly_income,
        mortgage_left=new_mortgage_left,
        mortgage_rate=prev.mortgage_rate,
        mortgage_months=new_mortgage_months,
        annual_rent_increase_rate=prev.annual_rent_increase_rate,
    )
