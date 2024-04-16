from datetime import date
from decimal import Decimal
from typing import Generator
from fire.properties import InvestmentProperty

from fire.simulations import FireSimulation, simulate_next


def test_simulation_when_enough_not_enough_cash() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("10_000"),
        investment_properties=[],
        cash=Decimal("10_000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("11_000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "bonds_investments": 9_000,
        "wealth_inc_properties": 9_000.0,
        "properties_monthly_mortgage": 0,
        "investment_properties": [],
        "cash": 0,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "stock_return_rate": 0,
        "bonds_return_rate": 0,
        "annual_income_increase_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "properties_net_cash_value": 0,
        "liquid_wealth": 9000.0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }


def test_simulation_when_enough_cash_and_stock_and_bonds() -> None:
    init = FireSimulation(
        stock_investments=Decimal("10_000"),
        bonds_investments=Decimal("10_000"),
        investment_properties=[],
        cash=Decimal("10_000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("21_000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 9_000,
        "bonds_investments": 0,
        "investment_properties": [],
        "wealth_inc_properties": 9_000.0,
        "properties_monthly_mortgage": 0,
        "cash": 0,
        "liquid_wealth": 9000,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "stock_return_rate": 0,
        "annual_income_increase_rate": 0,
        "monthly_expenses": 21_000,
        "monthly_income": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_net_cash_value": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }


def test_simulation_when_not_enough_cash_and_stock() -> None:
    init = FireSimulation(
        stock_investments=Decimal("10_000"),
        bonds_investments=Decimal("10_000"),
        investment_properties=[],
        cash=Decimal("10_000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("31_000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "investment_properties": [],
        "cash": -1000,
        "wealth_inc_properties": -1000.0,
        "properties_monthly_mortgage": 0,
        "liquid_wealth": -1000,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "annual_income_increase_rate": 0,
        "monthly_inflation_rate": 0.0,
        "stock_return_rate": 0,
        "monthly_expenses": 31_000,
        "monthly_income": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_net_cash_value": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }


def test_when_monthly_income_is_present() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("10_000"),
        investment_properties=[],
        cash=Decimal("10_000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("21_000"),
        monthly_income=Decimal("11_000"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "bonds_investments": 10_000,
        "investment_properties": [],
        "cash": 0,
        "liquid_wealth": 10_000,
        "wealth_inc_properties": 10_000.0,
        "properties_monthly_mortgage": 0,
        "stock_return_rate": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "monthly_expenses": 21_000,
        "monthly_income": 11_000,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_net_cash_value": 0,
        "properties_mortgage_left": 0,
        "annual_income_increase_rate": 0,
        "date": date(2021, 2, 1),
    }


def test_when_monthly_income_from_properties_without_mortgage_is_present() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        investment_properties=[
            InvestmentProperty(
                mortgage_left=Decimal("0"),
                mortgage_rate=Decimal("0"),
                mortgage_months=0,
                market_value=Decimal("100_000"),
                monthly_income=Decimal("2_000"),
            )
        ],
        annual_property_appreciation_rate=Decimal("0.1"),
        cash=Decimal("10_000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("11_000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    expected = {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_monthly_income": 2_000,
        "cash": 1_000,
        "investment_properties": [
            {
                "mortgage_left": Decimal(0),
                "mortgage_rate": Decimal(0),
                "mortgage_months": 0,
                "market_value": Decimal("100_833.33"),
                "monthly_income": Decimal(2_000),
                "monthly_interest": 0,
                "monthly_payment": 0,
                "annual_rent_increase_rate": Decimal("0.0"),
            }
        ],
        "stock_return_rate": 0,
        "annual_income_increase_rate": 0,
        "liquid_wealth": 1000,
        "wealth_inc_properties": 101833.33,
        "properties_monthly_mortgage": 0,
        "properties_market_value": 100833.33,
        "properties_net_cash_value": 100833.33,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0.1,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }

    assert next_sim.to_dict() == expected


def test_when_monthly_income_from_properties_with_mortgage_is_present() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        investment_properties=[
            InvestmentProperty(
                mortgage_left=Decimal("100000"),
                mortgage_rate=Decimal("10"),
                mortgage_months=100,
                market_value=Decimal("100000"),
                monthly_income=Decimal("2000"),
            )
        ],
        annual_property_appreciation_rate=Decimal("0.1"),
        cash=Decimal("10000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("11000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    expected = {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_monthly_income": 2_000,
        "cash": 1_000,
        "investment_properties": [
            {
                "mortgage_left": Decimal("99_355.52"),
                "mortgage_rate": Decimal("10"),
                "mortgage_months": 99,
                "market_value": Decimal("100_833.33"),
                "monthly_income": Decimal(2_000),
                "monthly_interest": Decimal("827.96"),
                "monthly_payment": Decimal("1477.81"),
                "annual_rent_increase_rate": Decimal("0.0"),
            }
        ],
        "stock_return_rate": 0,
        "annual_income_increase_rate": 0,
        "liquid_wealth": 1000,
        "wealth_inc_properties": 2477.81,
        "properties_monthly_mortgage": 1477.81,
        "properties_market_value": 100833.33,
        "properties_net_cash_value": 1477.81,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0.1,
        "properties_mortgage_left": 99355.52,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "date": date(2021, 2, 1),
    }

    assert next_sim.to_dict() == expected


def test_when_monthly_income_from_properties_with_mortgage_is_present_and_need_to_sell() -> (
    None
):
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        investment_properties=[
            InvestmentProperty(
                mortgage_left=Decimal("0"),
                mortgage_rate=Decimal("0"),
                mortgage_months=0,
                market_value=Decimal("100_000"),
                monthly_income=Decimal("2_000"),
            )
        ],
        annual_property_appreciation_rate=Decimal("0"),
        cash=Decimal("10_000"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("15_000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)
    # 21348
    expected = {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_monthly_income": 0,
        "annual_income_increase_rate": 0,
        "cash": 97_000,
        "investment_properties": [],
        "stock_return_rate": 0,
        "liquid_wealth": 97_000,
        "wealth_inc_properties": 97_000,
        "properties_monthly_mortgage": 0,
        "properties_market_value": 0,
        "properties_net_cash_value": 0,
        "monthly_expenses": 15_000,
        "monthly_income": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": Decimal("0"),
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }

    assert next_sim.to_dict() == expected


def test_when_applying_stock_investment_return_rates() -> None:
    init = FireSimulation(
        stock_investments=Decimal("100000"),
        bonds_investments=Decimal("0"),
        investment_properties=[],
        cash=Decimal("11000"),
        stock_return_rate=Decimal("0.05"),
        monthly_expenses=Decimal("11000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 100_416.67,
        "bonds_investments": 0,
        "annual_income_increase_rate": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "investment_properties": [],
        "liquid_wealth": 100416.67,
        "properties_monthly_mortgage": 0,
        "wealth_inc_properties": 100416.67,
        "stock_return_rate": 0.05,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0.00,
        "properties_net_cash_value": 0,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }


def test_when_applying_bonds_investment_return_rates() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("100000"),
        investment_properties=[],
        cash=Decimal("11000"),
        stock_return_rate=Decimal("0"),
        bonds_return_rate=Decimal("0.03"),
        monthly_expenses=Decimal("11000"),
        monthly_income=Decimal("0"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "bonds_investments": 100_250,
        "annual_income_increase_rate": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "investment_properties": [],
        "liquid_wealth": 100_250,
        "properties_monthly_mortgage": 0,
        "wealth_inc_properties": 100250.0,
        "stock_return_rate": 0,
        "bonds_return_rate": 0.03,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0.0,
        "annual_property_appreciation_rate": 0.00,
        "properties_net_cash_value": 0,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }


def test_when_applying_inflation_rate_to_monthly_expenses() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        investment_properties=[],
        cash=Decimal("11_000"),
        stock_return_rate=Decimal("0"),
        bonds_return_rate=Decimal("0"),
        monthly_expenses=Decimal("11_000"),
        monthly_income=Decimal("0"),
        annual_inflation_rate=Decimal("0.03"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "annual_income_increase_rate": 0,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": -27.5,
        "investment_properties": [],
        "liquid_wealth": -27.5,
        "properties_monthly_mortgage": 0,
        "wealth_inc_properties": -27.5,
        "stock_return_rate": 0,
        "bonds_return_rate": 0,
        "monthly_expenses": 11_027.5,
        "monthly_income": 0,
        "annual_inflation_rate": 0.03,
        "monthly_inflation_rate": 0.0025,
        "annual_property_appreciation_rate": 0.00,
        "properties_net_cash_value": 0,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 2, 1),
    }


def test_that_surplus_money_is_invested() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        investment_properties=[],
        cash=Decimal("30_000"),
        stock_return_rate=Decimal("0"),
        bonds_return_rate=Decimal("0"),
        monthly_expenses=Decimal("10_000"),
        monthly_income=Decimal("0"),
        annual_inflation_rate=Decimal("0"),
        annual_property_appreciation_rate=Decimal("0.01"),
        invest_cash_surplus=True,
        invest_cash_surplus_strategy="80-20",
        invest_cash_threshold=Decimal("10_000"),
        date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 8_000,
        "annual_income_increase_rate": 0,
        "bonds_investments": 2_000,
        "investment_properties": [],
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 10000,
        "liquid_wealth": 20_000,
        "properties_monthly_mortgage": 0,
        "wealth_inc_properties": 20000.0,
        "stock_return_rate": 0,
        "bonds_return_rate": 0,
        "monthly_expenses": 10000,
        "monthly_income": 0,
        "annual_inflation_rate": 0.00,
        "monthly_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.01,
        "properties_net_cash_value": 0,
        "properties_mortgage_left": 0,
        "invest_cash_surplus": True,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 10_000,
        "date": date(2021, 2, 1),
    }


def test_simulation_when_annual_increase_happens() -> None:
    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        annual_income_increase_rate=Decimal("0.01"),
        investment_properties=[],
        cash=Decimal("0"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("10_000"),
        monthly_income=Decimal("10_000"),
        date=date(2020, 12, 1),
    )

    next_sim = simulate_next(init)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "wealth_inc_properties": 100,
        "liquid_wealth": 100.0,
        "properties_monthly_mortgage": 0,
        "investment_properties": [],
        "cash": 100,
        "monthly_expenses": 10_000,
        "annual_income_increase_rate": 0.01,
        "monthly_income": 10_100,
        "stock_return_rate": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0,
        "monthly_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "properties_net_cash_value": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 1, 1),
    }


def test_simulation_when_inflation_generator_is_provided() -> None:
    def inflation_rate_gen() -> Generator[Decimal, None, None]:
        while True:
            yield Decimal("0.01")
            yield Decimal("0.02")

    init = FireSimulation(
        stock_investments=Decimal("0"),
        bonds_investments=Decimal("0"),
        annual_income_increase_rate=Decimal("0"),
        investment_properties=[],
        cash=Decimal("0"),
        stock_return_rate=Decimal("0"),
        monthly_expenses=Decimal("10_000"),
        monthly_income=Decimal("10_000"),
        date=date(2020, 12, 1),
    )

    gen = inflation_rate_gen()
    next_sim = simulate_next(init, inflation_rate_gen=gen)

    assert next_sim.to_dict() == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "wealth_inc_properties": -100,
        "liquid_wealth": -100,
        "properties_monthly_mortgage": 0,
        "investment_properties": [],
        "cash": -100,
        "monthly_expenses": 10_100,
        "annual_income_increase_rate": 0,
        "monthly_income": 10_000,
        "stock_return_rate": 0,
        "bonds_return_rate": 0,
        "annual_inflation_rate": 0.12,
        "monthly_inflation_rate": 0.01,
        "annual_property_appreciation_rate": 0,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "properties_net_cash_value": 0,
        "properties_mortgage_left": 0,
        "date": date(2021, 1, 1),
    }

    next_sim_2 = simulate_next(next_sim, inflation_rate_gen=gen)
    d2 = next_sim_2.to_dict()
    assert d2["annual_inflation_rate"] == 0.24
