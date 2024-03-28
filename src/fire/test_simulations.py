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
        return_rate_from_investment=0.05,
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
        "return_rate_from_investment": 0.05,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "start_date": date(2021, 2, 1),
    }


def test_simulation_when_enough_cash_and_stock_and_bonds() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=10_000,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0.05,
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
        "return_rate_from_investment": 0.05,
        "monthly_expenses": 21_000,
        "monthly_income": 0,
        "start_date": date(2021, 2, 1),
    }


def test_simulation_when_not_enough_cash_and_stock() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=10_000,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0.05,
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
        "return_rate_from_investment": 0.05,
        "monthly_expenses": 31_000,
        "monthly_income": 0,
        "start_date": date(2021, 2, 1),
    }


def test_when_monthly_income_is_present() -> None:
    init = FireSimulation(
        stock_investments=10_000,
        bonds_investments=0,
        properties_market_value=0,
        properties_monthly_income=0,
        cash=10_000,
        return_rate_from_investment=0.05,
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
        "return_rate_from_investment": 0.05,
        "monthly_expenses": 21_000,
        "monthly_income": 11_000,
        "start_date": date(2021, 2, 1),
    }


def test_when_monthly_dividend_from_properties_is_present() -> None:
    init = FireSimulation(
        stock_investments=0,
        bonds_investments=0,
        properties_market_value=100_000,
        properties_monthly_income=2_000,
        cash=10_000,
        return_rate_from_investment=0.05,
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
        "return_rate_from_investment": 0.05,
        "monthly_expenses": 11_000,
        "monthly_income": 0,
        "start_date": date(2021, 2, 1),
    }
