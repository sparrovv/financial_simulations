from dataclasses import dataclass, asdict, field, replace
from datetime import date
from typing import Literal
from .mortgage import calculate_monthly_payment
from decimal import Decimal


@dataclass
class InvestmentProperty:
    market_value: Decimal
    monthly_income: Decimal
    mortgage_left: Decimal
    mortgage_rate: Decimal
    mortgage_months: int

    def is_with_mortgage(self) -> bool:
        return self.mortgage_left > 0

    def net_cash_value(self) -> Decimal:
        return self.market_value - self.mortgage_left

    def to_dict(self):
        return asdict(self) | {"net_cash_value": self.net_cash_value()}


def simulate_next_property_month(
    prev: InvestmentProperty, annual_property_appreciation_rate: Decimal
) -> InvestmentProperty:
    new_market_value = round(
        prev.market_value
        + (prev.market_value * annual_property_appreciation_rate / Decimal(12)),
        2,
    )

    if prev.is_with_mortgage() is False:
        return replace(prev, market_value=new_market_value)

    monthly_payment, monthly_interest = calculate_monthly_payment(
        principal=prev.mortgage_left,
        rate=prev.mortgage_rate,
        number_of_months_left=prev.mortgage_months,
    )

    # calculate the principal
    monthly_principal = monthly_payment - monthly_interest

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
    stock_investments: float
    bonds_investments: float

    cash: float
    monthly_expenses: float
    monthly_income: float
    start_date: date
    return_rate_from_investment: float

    investment_properties: list[InvestmentProperty] = field(default_factory=list)
    return_rate_from_bonds: float = 0
    annual_inflation_rate: float = 0
    # this should be more or less the same as the inflation rate
    annual_property_appreciation_rate: Decimal = Decimal(0)
    invest_cash_surplus: bool = False
    # this says what's the threshold over which the cash should be invested based on the strategy
    invest_cash_threshold: float = 0
    invest_cash_surplus_strategy: Literal["80-20", "100", "60-40", "50-50"] = "80-20"

    @property
    def properties_market_value(self) -> float:
        return sum([float(p.market_value) for p in self.investment_properties])

    @property
    def properties_monthly_income(self) -> float:
        return sum([float(p.monthly_income) for p in self.investment_properties])

    @property
    def properties_net_cash_value(self) -> float:
        return sum([float(p.net_cash_value()) for p in self.investment_properties])

    @property
    def wealth(self) -> float:
        return (
            self.stock_investments
            + self.bonds_investments
            + self.properties_net_cash_value
            + self.cash
        )

    def to_dict(self):
        return asdict(self) | {
            "wealth": self.wealth,
            "properties_market_value": self.properties_market_value,
            "properties_monthly_income": self.properties_monthly_income,
            "properties_net_cash_value": self.properties_net_cash_value,
        }


def run_simulation(init: FireSimulation, months: int) -> list[FireSimulation]:
    simulations = [init]
    for _ in range(months):
        next_sim = simulate_next(simulations[-1])
        simulations.append(next_sim)
    return simulations


def simulate_next(prev: FireSimulation) -> FireSimulation:
    # add one month to the start date, year should change if month is 12

    new_start_date = prev.start_date.replace(
        month=prev.start_date.month + 1 if prev.start_date.month < 12 else 1,
        year=(
            prev.start_date.year + 1
            if prev.start_date.month == 12
            else prev.start_date.year
        ),
    )

    new_investment_properties = [
        simulate_next_property_month(prop, prev.annual_property_appreciation_rate)
        for prop in prev.investment_properties
    ]

    # total expenses should include inflation rate
    total_monthly_expenses = prev.monthly_expenses * (
        1 + prev.annual_inflation_rate / 12
    )

    # total income
    total_monthly_cash = (
        prev.cash + prev.monthly_income + prev.properties_monthly_income
    )

    new_properties_net_cash_value = sum(
        [float(p.net_cash_value()) for p in new_investment_properties]
    )

    new_bonds_investments = round(
        prev.bonds_investments
        + (prev.bonds_investments * prev.return_rate_from_bonds / 12),
        2,
    )
    # if there are any stock investments, calculate the return rate and add it to the stock investments
    new_stock_investments = round(
        prev.stock_investments
        + (prev.stock_investments * prev.return_rate_from_investment / 12),
        2,
    )

    if total_monthly_cash > total_monthly_expenses:
        new_cash = total_monthly_cash - total_monthly_expenses
    elif (total_monthly_cash + new_stock_investments) > total_monthly_expenses:
        new_cash = 0
        cash_needed = total_monthly_expenses - total_monthly_cash
        new_stock_investments -= cash_needed
    elif (
        total_monthly_cash + new_stock_investments + new_bonds_investments
    ) > total_monthly_expenses:
        new_cash = 0
        cash_needed = (
            total_monthly_expenses - total_monthly_cash - new_stock_investments
        )
        new_stock_investments = 0
        new_bonds_investments -= cash_needed
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

        new_cash = 0
        new_cash += float(to_delete_property.net_cash_value())
        # new_properties_net_cash_value = sum(
        #     [float(p.net_cash_value()) for p in new_investment_properties]
        # )

        cash_needed = (
            total_monthly_expenses
            - total_monthly_cash
            - new_stock_investments
            - new_bonds_investments
        )
        new_stock_investments = 0
        new_bonds_investments = 0
        new_cash -= cash_needed
    else:
        cash_needed = (
            total_monthly_expenses
            - total_monthly_cash
            - new_stock_investments
            - new_bonds_investments
        )
        new_stock_investments = 0
        new_bonds_investments = 0
        new_cash = -cash_needed

    # if there's a surplus of cash, we should invest it
    if prev.invest_cash_surplus:
        amount_over_threshold = new_cash - prev.invest_cash_threshold

        if amount_over_threshold > 0:
            if prev.invest_cash_surplus_strategy == "80-20":
                new_stock_investments += amount_over_threshold * 0.8
                new_bonds_investments += amount_over_threshold * 0.2
            elif prev.invest_cash_surplus_strategy == "100":
                new_stock_investments += amount_over_threshold
            elif prev.invest_cash_surplus_strategy == "60-40":
                new_stock_investments += amount_over_threshold * 0.6
                new_bonds_investments += amount_over_threshold * 0.4
            elif prev.invest_cash_surplus_strategy == "50-50":
                new_stock_investments += amount_over_threshold * 0.5
                new_bonds_investments += amount_over_threshold * 0.5

            new_cash -= amount_over_threshold

    return FireSimulation(
        stock_investments=new_stock_investments,
        investment_properties=new_investment_properties,
        bonds_investments=new_bonds_investments,
        cash=new_cash,
        return_rate_from_investment=prev.return_rate_from_investment,
        return_rate_from_bonds=prev.return_rate_from_bonds,
        monthly_expenses=total_monthly_expenses,
        monthly_income=prev.monthly_income,
        annual_inflation_rate=prev.annual_inflation_rate,
        annual_property_appreciation_rate=prev.annual_property_appreciation_rate,
        invest_cash_surplus=prev.invest_cash_surplus,
        invest_cash_threshold=prev.invest_cash_threshold,
        invest_cash_surplus_strategy=prev.invest_cash_surplus_strategy,
        start_date=new_start_date,
    )
