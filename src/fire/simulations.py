from dataclasses import dataclass, asdict, field, replace
from datetime import date
from typing import Literal
from .mortgage import calculate_monthly_payment
from decimal import Decimal, getcontext
from logging import getLogger

getcontext().prec = 26

logger = getLogger(__name__)


@dataclass
class InvestmentProperty:
    market_value: Decimal
    monthly_income: Decimal
    mortgage_left: Decimal
    mortgage_rate: Decimal
    mortgage_months: int
    monthly_interest: Decimal = Decimal("0")
    monthly_payment: Decimal = Decimal("0")

    def is_with_mortgage(self) -> bool:
        return self.mortgage_left > 0

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
    prev: InvestmentProperty, annual_property_appreciation_rate: Decimal
) -> InvestmentProperty:
    new_market_value = round(
        prev.market_value
        + (prev.market_value * annual_property_appreciation_rate / Decimal("12")),
        2,
    )

    if prev.is_with_mortgage() is False:
        return replace(prev, market_value=new_market_value)

    # calculate the principal
    monthly_principal = prev.monthly_payment - prev.monthly_interest

    new_mortgage_left = prev.mortgage_left - monthly_principal
    new_mortgage_months = prev.mortgage_months - 1

    return InvestmentProperty(
        market_value=new_market_value,
        monthly_income=prev.monthly_income,
        mortgage_left=new_mortgage_left,
        mortgage_rate=prev.mortgage_rate,
        mortgage_months=new_mortgage_months,
    )


@dataclass
class FireSimulation:
    stock_investments: Decimal
    bonds_investments: Decimal

    cash: Decimal
    monthly_expenses: Decimal
    monthly_income: Decimal
    date: date
    stock_return_rate: Decimal

    investment_properties: list[InvestmentProperty] = field(default_factory=list)
    bonds_return_rate: Decimal = Decimal(0)

    annual_inflation_rate: Decimal = Decimal(0)
    annual_income_increase_rate: Decimal = Decimal(0)
    # this should be more or less the same as the inflation rate
    annual_property_appreciation_rate: Decimal = Decimal(0)
    invest_cash_surplus: bool = False
    # this says what's the threshold over which the cash should be invested based on the strategy
    invest_cash_threshold: Decimal = Decimal(0)
    invest_cash_surplus_strategy: Literal["80-20", "100", "60-40", "50-50"] = "80-20"

    @property
    def properties_market_value(self) -> Decimal:
        return sum([p.market_value for p in self.investment_properties])

    @property
    def properties_monthly_income(self) -> Decimal:
        return sum([p.monthly_income for p in self.investment_properties])

    @property
    def properties_net_cash_value(self) -> Decimal:
        return sum([p.net_cash_value() for p in self.investment_properties])

    @property
    def liquid_wealth(self) -> Decimal:
        return self.stock_investments + self.bonds_investments + self.cash

    @property
    def wealth_inc_properties(self) -> Decimal:
        return (
            self.stock_investments
            + self.bonds_investments
            + self.properties_net_cash_value
            + self.cash
        )

    @property
    def properties_monthly_mortgage(self) -> Decimal:
        return sum(
            [
                p.monthly_payment
                for p in self.investment_properties
                if p.is_with_mortgage()
            ]
        )

    def to_dict(self):
        return asdict(self) | {
            "liquid_wealth": self.liquid_wealth,
            "wealth_inc_properties": self.wealth_inc_properties,
            "properties_monthly_mortgage": self.properties_monthly_mortgage,
            "properties_market_value": self.properties_market_value,
            "properties_monthly_income": self.properties_monthly_income,
            "properties_net_cash_value": self.properties_net_cash_value,
        }


def run_simulation(init: FireSimulation, months: int) -> list[FireSimulation]:
    simulations = [init]
    for _ in range(months):
        next_sim = simulate_next(simulations[-1])
        if next_sim.wealth_inc_properties < 0:
            break

        simulations.append(next_sim)
    return simulations


def simulate_next(prev: FireSimulation) -> FireSimulation:
    # add one month to the start date, year should change if month is 12

    new_date = prev.date.replace(
        month=prev.date.month + 1 if prev.date.month < 12 else 1,
        year=(prev.date.year + 1 if prev.date.month == 12 else prev.date.year),
    )

    new_investment_properties = [
        simulate_next_property_month(prop, prev.annual_property_appreciation_rate)
        for prop in prev.investment_properties
    ]

    # total expenses should include inflation rate
    total_monthly_expenses = prev.monthly_expenses * (
        1 + prev.annual_inflation_rate / Decimal("12")
    )
    # we have annula income increase rate, so we should increase the monthly income once a year
    # we could increase it monthly, but in reality it's more likely to increase once a year, so we'll do that
    # if prev.date.month == 1:
    new_monthly_income = prev.monthly_income
    if new_date.month == 1:
        new_monthly_income = prev.monthly_income * (
            1 + prev.annual_income_increase_rate
        )

    # total income
    total_monthly_cash = prev.cash + new_monthly_income + prev.properties_monthly_income

    new_properties_net_cash_value = sum(
        [p.net_cash_value() for p in new_investment_properties]
    )

    new_bonds_investments = prev.bonds_investments + (
        prev.bonds_investments * prev.bonds_return_rate / Decimal("12")
    )
    # if there are any stock investments, calculate the return rate and add it to the stock investments
    new_stock_investments = prev.stock_investments + (
        prev.stock_investments * prev.stock_return_rate / Decimal("12")
    )

    if total_monthly_cash > total_monthly_expenses:
        new_cash = total_monthly_cash - total_monthly_expenses
    elif (total_monthly_cash + new_bonds_investments) > total_monthly_expenses:
        new_cash = Decimal("0")
        cash_needed = total_monthly_expenses - total_monthly_cash
        new_bonds_investments -= cash_needed
    elif (
        total_monthly_cash + new_bonds_investments + new_stock_investments
    ) > total_monthly_expenses:
        new_cash = Decimal("0")
        cash_needed = (
            total_monthly_expenses - total_monthly_cash - new_bonds_investments
        )
        new_bonds_investments = Decimal("0")
        new_stock_investments -= cash_needed
    elif (
        total_monthly_cash
        + new_stock_investments
        + new_bonds_investments
        + new_properties_net_cash_value
    ) > total_monthly_expenses:
        # we need to sell a property, if we have one then we sell it
        # if we have more than one, we sell the one with the lowest net cash value
        # then we add the cash to the cash account

        to_delete_property = min(
            new_investment_properties, key=lambda p: p.net_cash_value()
        )
        new_investment_properties.remove(to_delete_property)

        new_cash = Decimal("0")
        new_cash += to_delete_property.net_cash_value()

        cash_needed = (
            total_monthly_expenses
            - total_monthly_cash
            - new_stock_investments
            - new_bonds_investments
        )
        new_stock_investments = Decimal("0")
        new_stock_investments = Decimal("0")
        new_cash -= cash_needed
    else:
        cash_needed = (
            total_monthly_expenses
            - total_monthly_cash
            - new_stock_investments
            - new_bonds_investments
        )
        new_bonds_investments = Decimal("0")
        new_stock_investments = Decimal("0")
        new_cash = -cash_needed

    # if there's a surplus of cash, we should invest it
    if prev.invest_cash_surplus:
        amount_over_threshold = new_cash - prev.invest_cash_threshold

        if amount_over_threshold > 0:
            if prev.invest_cash_surplus_strategy == "80-20":
                new_stock_investments += amount_over_threshold * Decimal("0.8")
                new_bonds_investments += amount_over_threshold * Decimal("0.2")
            elif prev.invest_cash_surplus_strategy == "100":
                new_stock_investments += amount_over_threshold
            elif prev.invest_cash_surplus_strategy == "60-40":
                new_stock_investments += amount_over_threshold * Decimal("0.6")
                new_bonds_investments += amount_over_threshold * Decimal("0.4")
            elif prev.invest_cash_surplus_strategy == "50-50":
                new_stock_investments += amount_over_threshold * Decimal("0.5")
                new_bonds_investments += amount_over_threshold * Decimal("0.5")

            new_cash -= amount_over_threshold

    return FireSimulation(
        stock_investments=round(new_stock_investments, 2),
        investment_properties=new_investment_properties,
        bonds_investments=round(new_bonds_investments, 2),
        cash=new_cash,
        stock_return_rate=prev.stock_return_rate,
        bonds_return_rate=prev.bonds_return_rate,
        monthly_expenses=total_monthly_expenses,
        monthly_income=new_monthly_income,
        annual_inflation_rate=prev.annual_inflation_rate,
        annual_property_appreciation_rate=prev.annual_property_appreciation_rate,
        invest_cash_surplus=prev.invest_cash_surplus,
        invest_cash_threshold=prev.invest_cash_threshold,
        invest_cash_surplus_strategy=prev.invest_cash_surplus_strategy,
        annual_income_increase_rate=prev.annual_income_increase_rate,
        date=new_date,
    )
