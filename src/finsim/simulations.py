from dataclasses import dataclass, asdict, field, replace
from datetime import date
from typing import Generator, Literal, Optional

from finsim.properties import InvestmentProperty, simulate_next_property_month
from decimal import Decimal, getcontext
from logging import getLogger

getcontext().prec = 26

logger = getLogger(__name__)


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
    monthly_inflation_rate: Decimal = Decimal(0)
    annual_income_increase_rate: Decimal = Decimal(0)
    # this should be more or less the same as the inflation rate
    annual_property_appreciation_rate: Decimal = Decimal(0)
    invest_cash_surplus: bool = False
    # this says what's the threshold over which the cash should be invested based on the strategy
    invest_cash_threshold: Decimal = Decimal(0)
    invest_cash_surplus_strategy: Literal["80-20", "100", "60-40", "50-50"] = "80-20"

    @property
    def properties_market_value(self) -> Decimal:
        return Decimal(sum([p.market_value for p in self.investment_properties]))

    @property
    def properties_monthly_income(self) -> Decimal:
        return Decimal(sum([p.monthly_income for p in self.investment_properties]))

    @property
    def properties_net_cash_value(self) -> Decimal:
        return Decimal(sum([p.net_cash_value() for p in self.investment_properties]))

    @property
    def properties_mortgage_left(self) -> Decimal:
        return Decimal(sum([p.mortgage_left for p in self.investment_properties]))

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
        return Decimal(
            sum(
                [
                    p.monthly_payment
                    for p in self.investment_properties
                    if p.is_with_mortgage()
                ]
            )
        )

    def to_dict(self) -> dict:

        to_return = asdict(self) | {
            "liquid_wealth": self.liquid_wealth,
            "wealth_inc_properties": self.wealth_inc_properties,
            "properties_monthly_mortgage": self.properties_monthly_mortgage,
            "properties_market_value": self.properties_market_value,
            "properties_monthly_income": self.properties_monthly_income,
            "properties_net_cash_value": self.properties_net_cash_value,
            "properties_mortgage_left": self.properties_mortgage_left,
        }

        for k, v in to_return.items():
            if isinstance(v, Decimal):
                to_return[k] = float(v)

        return to_return


def run_simulation(
    init: FireSimulation,
    months: int,
    inflation_rate_gen: Optional[Generator[Decimal, None, None]] = None,
) -> list[FireSimulation]:
    simulations = [init]
    for _ in range(months):
        next_sim = simulate_next(simulations[-1], inflation_rate_gen=inflation_rate_gen)
        if next_sim.wealth_inc_properties < 0:
            break

        simulations.append(next_sim)
    return simulations


def run_fire_simulation(
    init: FireSimulation,
    expected_number_of_months: int,
    inflation_rate_gen: Optional[Generator[Decimal, None, None]] = None,
) -> tuple[list[FireSimulation], int]:
    """
    The fire simulation tries to find a point when the wealth is enough to sustain the monthly expenses for the expected number of months.

    On every month, try to zero out the income and break when the simulation reaches the expected number of months
    """
    final_sim = []
    number_of_months = 0

    for i in range(expected_number_of_months):
        number_of_months += 1
        simulations = [init]
        for x in range(expected_number_of_months):
            if x > i:
                # update income to 0
                prev = replace(simulations[-1], monthly_income=Decimal("0"))
                next_sim = simulate_next(prev, inflation_rate_gen=inflation_rate_gen)
            else:
                next_sim = simulate_next(
                    simulations[-1], inflation_rate_gen=inflation_rate_gen
                )

            if next_sim.wealth_inc_properties <= 0:
                break

            simulations.append(next_sim)

        final_sim = simulations
        if len(simulations) >= (expected_number_of_months - 2):
            break

    return final_sim, number_of_months


def simulate_next(
    prev: FireSimulation,
    inflation_rate_gen: Optional[Generator[Decimal, None, None]] = None,
) -> FireSimulation:
    # add one month to the start date, year should change if month is 12

    new_date = prev.date.replace(
        month=prev.date.month + 1 if prev.date.month < 12 else 1,
        year=(prev.date.year + 1 if prev.date.month == 12 else prev.date.year),
    )

    new_investment_properties = [
        simulate_next_property_month(
            prop, prev.annual_property_appreciation_rate, sim_date=new_date
        )
        for prop in prev.investment_properties
    ]

    annual_inflation_rate = prev.annual_inflation_rate
    monthly_inflation_rate = annual_inflation_rate / Decimal("12")
    if inflation_rate_gen:
        monthly_inflation_rate = next(inflation_rate_gen)
        annual_inflation_rate = monthly_inflation_rate * Decimal("12")

    # total expenses should include inflation rate
    total_monthly_expenses = prev.monthly_expenses * (1 + monthly_inflation_rate)
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
        cash=round(new_cash, 2),
        stock_return_rate=prev.stock_return_rate,
        bonds_return_rate=prev.bonds_return_rate,
        monthly_expenses=round(total_monthly_expenses, 2),
        monthly_income=round(new_monthly_income, 2),
        annual_inflation_rate=annual_inflation_rate,
        monthly_inflation_rate=monthly_inflation_rate,
        annual_property_appreciation_rate=prev.annual_property_appreciation_rate,
        invest_cash_surplus=prev.invest_cash_surplus,
        invest_cash_threshold=prev.invest_cash_threshold,
        invest_cash_surplus_strategy=prev.invest_cash_surplus_strategy,
        annual_income_increase_rate=prev.annual_income_increase_rate,
        date=new_date,
    )
