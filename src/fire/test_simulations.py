from dataclasses import asdict
from datetime import date

from simulations import FireSimulation, simulate_next


def test_simulation_when_enough_not_enough_cash() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=0,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0,
        monthly_expenses=11_000,
        monthly_income=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 9_000,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "return_rate_from_investment": 0,
        "return_rate_from_bonds": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_simulation_when_enough_cash_and_stock_and_bonds() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=10_000,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0,
        monthly_expenses=21_000,
        monthly_income=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 9_000,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "return_rate_from_investment": 0,
        "monthly_expenses": 21_000,
        "monthly_income": 0,
        "return_rate_from_bonds": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_simulation_when_not_enough_cash_and_stock() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=10_000,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0,
        monthly_expenses=31_000,
        monthly_income=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": -1000,
        "return_rate_from_investment": 0,
        "monthly_expenses": 31_000,
        "monthly_income": 0,
        "return_rate_from_bonds": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_monthly_income_is_present() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=0,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0,
        monthly_expenses=21_000,
        monthly_income=11_000,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 10_000,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "return_rate_from_investment": 0,
        "monthly_expenses": 21_000,
        "monthly_income": 11_000,
        "return_rate_from_bonds": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_monthly_dividend_from_properties_is_present() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=0,
        properties_market_value=100_000,
        properties_monthly_income=2_000,
        cash=10_000,
        return_rate_from_investment=0,
        monthly_expenses=11_000,
        monthly_income=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_market_value": 100_000,
        "properties_monthly_income": 2_000,
        "cash": 1_000,
        "return_rate_from_investment": 0,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "return_rate_from_bonds": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_applying_stock_investment_return_rates() -> None:
    init = FireSimulation(
        stock_investments=100_000,
        bonds_investments=0,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=11_000,
        return_rate_from_investment=0.05,
        monthly_expenses=11_000,
        monthly_income=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 100_416.67,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "return_rate_from_investment": 0.05,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "return_rate_from_bonds": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_applying_bonds_investment_return_rates() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=100_000,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=11_000,
        return_rate_from_investment=0,
        return_rate_from_bonds=0.03,
        monthly_expenses=11_000,
        monthly_income=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 100_250,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 0,
        "return_rate_from_investment": 0,
        "return_rate_from_bonds": 0.03,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "annual_inflation_rate": 0,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_applying_inflation_rate_to_monthly_expenses() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=0,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=11_000,
        return_rate_from_investment=0,
        return_rate_from_bonds=0,
        monthly_expenses=11_000,
        monthly_income=0,
        annual_inflation_rate=0.03,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": -27.5,
        "return_rate_from_investment": 0,
        "return_rate_from_bonds": 0,
        "monthly_expenses": 11_027.5,
        "monthly_income": 0,
        "annual_inflation_rate": 0.03,
        "annual_property_appreciation_rate": 0.00,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_properties_market_value_is_considered() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=0,
        properties_market_value=200_000,
        properties_monthly_income=0,
        cash=11_000,
        return_rate_from_investment=0,
        return_rate_from_bonds=0,
        monthly_expenses=15_000,
        monthly_income=0,
        annual_inflation_rate=0,
        annual_property_appreciation_rate=0,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 196000.0,
        "return_rate_from_investment": 0,
        "return_rate_from_bonds": 0,
        "monthly_expenses": 15000,
        "monthly_income": 0,
        "annual_inflation_rate": 0.00,
        "annual_property_appreciation_rate": 0,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_properties_market_value_is_appreciated_considered() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=0,
        properties_market_value=200_000,
        properties_monthly_income=0,
        cash=11_000,
        return_rate_from_investment=0,
        return_rate_from_bonds=0,
        monthly_expenses=10_000,
        monthly_income=0,
        annual_inflation_rate=0,
        annual_property_appreciation_rate=0.01,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 0,
        "bonds_investments": 0,
        "properties_market_value": 200166.67,
        "properties_monthly_income": 0,
        "cash": 1000,
        "return_rate_from_investment": 0,
        "return_rate_from_bonds": 0,
        "monthly_expenses": 10000,
        "monthly_income": 0,
        "annual_inflation_rate": 0.00,
        "annual_property_appreciation_rate": 0.01,
        "invest_cash_surplus": False,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 0,
        "start_date": date(2021, 2, 1),
    }


def test_that_surplus_money_is_invested() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=0,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=30_000,
        return_rate_from_investment=0,
        return_rate_from_bonds=0,
        monthly_expenses=10_000,
        monthly_income=0,
        annual_inflation_rate=0,
        annual_property_appreciation_rate=0.01,
        invest_cash_surplus=True,
        invest_cash_surplus_strategy="80-20",
        invest_cash_threshold=10_000,
        start_date=date(2021, 1, 1),
    )

    next_sim = simulate_next(init)

    assert asdict(next_sim) == {
        "stock_investments": 8_000,
        "bonds_investments": 2_000,
        "properties_market_value": 0,
        "properties_monthly_income": 0,
        "cash": 10000,
        "return_rate_from_investment": 0,
        "return_rate_from_bonds": 0,
        "monthly_expenses": 10000,
        "monthly_income": 0,
        "annual_inflation_rate": 0.00,
        "annual_property_appreciation_rate": 0.01,
        "invest_cash_surplus": True,
        "invest_cash_surplus_strategy": "80-20",
        "invest_cash_threshold": 10_000,
        "start_date": date(2021, 2, 1),
    }
