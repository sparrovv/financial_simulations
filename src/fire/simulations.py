from dataclasses import dataclass, asdict
from datetime import date
from typing import Literal


@dataclass
class FireSimulation:
    stock_investments: float
    bonds_investments: float
    properties_market_value: float
    properties_monthly_income: float

    cash: float
    monthly_expenses: float
    monthly_income: float
    start_date: date
    return_rate_from_investment: float
    return_rate_from_bonds: float = 0
    annual_inflation_rate: float = 0
    # this should be more or less the same as the inflation rate
    annual_property_appreciation_rate: float = 0
    invest_cash_surplus: bool = False
    # this says what's the threshold over which the cash should be invested based on the strategy
    invest_cash_threshold: float = 0
    invest_cash_surplus_strategy: Literal["80-20", "100", "60-40", "50-50"] = "80-20"

    # monthly_mortgage
    # combined_mortgage_left: float
    # combined_mortgage_rate: float
    # combined_mortgage_months: int

    @property
    def wealth(self) -> float:
        return (
            self.stock_investments
            + self.bonds_investments
            + self.properties_market_value
            + self.cash
        )

    def to_dict(self):
        return asdict(self) | {"wealth": self.wealth}


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

    # total expenses should include inflation rate
    total_monthly_expenses = prev.monthly_expenses * (
        1 + prev.annual_inflation_rate / 12
    )

    # total income
    total_monthly_cash = (
        prev.cash + prev.monthly_income + prev.properties_monthly_income
    )
    prev.cash += prev.monthly_income + prev.properties_monthly_income

    new_properties_market_value = round(
        prev.properties_market_value
        + (prev.properties_market_value * prev.annual_property_appreciation_rate / 12),
        2,
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
        cash_needed = total_monthly_expenses - prev.cash
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
        + new_properties_market_value
    ) > total_monthly_expenses:
        # we need to sell a property, let's assume we sell the property for its market value, and we put all the cash in the bank
        # for now, but it should be invested in stocks or bonds and follow the investment strategy
        new_cash = 0
        new_cash += new_properties_market_value
        new_properties_market_value = 0

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
        bonds_investments=new_bonds_investments,
        properties_market_value=new_properties_market_value,
        properties_monthly_income=prev.properties_monthly_income,
        # combined_mortgage_left=prev.combined_mortgage_left,
        # combined_mortgage_rate=prev.combined_mortgage_rate,
        # combined_mortgage_months=prev.combined_mortgage_months,
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
