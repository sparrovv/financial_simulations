from dataclasses import dataclass
from pathlib import Path
import streamlit as st
import datetime
from datetime import timedelta
from decimal import Decimal
from fire.inflation import inflation_from_file_gen, random_inflation_gen
from fire.properties import InvestmentProperty
from view.conf import get_ranges


@dataclass
class BaseSidebarAttrs:
    monthly_income: Decimal
    monthly_expenses: Decimal
    stock_investment: Decimal
    bond_investment: Decimal
    cash: Decimal
    number_of_investment_properties: int
    investment_properties: list[InvestmentProperty]
    annual_inflation_rate: Decimal
    stock_return_rate: Decimal
    bonds_return_rate: Decimal
    annual_income_increase_rate: Decimal
    annual_property_appreciation_rate: Decimal
    invest_cash_surplus: bool
    invest_cash_surplus_strategy: str
    invest_cash_threshold: Decimal
    inflation_gen: any


@dataclass
class FireSidebarAttrs(BaseSidebarAttrs):
    current_age: int
    expected_age: int
    date_of_death: datetime.datetime
    expected_number_of_months: int


@dataclass
class SimpleSimSidebarAttrs(BaseSidebarAttrs):
    years: int
    currency_code: str


def simple_sim_sidebar(root_path: Path) -> SimpleSimSidebarAttrs:
    currency_code: str = st.selectbox(
        "Select currency code", ["USD", "PLN", "EUR"], index=0
    )  # type: ignore

    years = st.slider("How many years to simulate?", 1, 100, 20)
    f"Simulating for {years} years"

    base = _shared(root_path, currency_code)

    return SimpleSimSidebarAttrs(
        years=years,
        currency_code=currency_code,
        **base.__dict__,
    )


def fire_sidebar(root_path: Path) -> FireSidebarAttrs:
    currency_code: str = st.selectbox(
        "Select currency code", ["USD", "PLN", "EUR"], index=0
    )  # type: ignore

    current_age = st.slider("How old are you?", 0, 100, 38)
    expected_age = st.slider("Life expectancy?", 0, 100, 85)
    years = expected_age - current_age
    f"Simulating for {years} years"

    base = _shared(root_path, currency_code)
    return FireSidebarAttrs(
        current_age=current_age,
        expected_age=expected_age,
        date_of_death=datetime.datetime.now() + timedelta(days=years * 365),
        expected_number_of_months=years * 12,
        **base.__dict__,
    )


def _shared(root_path: Path, currency_code: str) -> tuple:

    r = get_ranges(currency_code)
    st.subheader("Provide monthly income and expenses:")
    monthly_income = st.slider("income", *r["monthly_income"])
    monthly_expenses = st.slider("monthly_expenses", *r["monthly_expenses"])

    st.subheader("Provide basic savings and expenses information:")
    stock_investment = st.slider("stock_investment", *r["stock_investment"])
    bond_investment = st.slider("bond_investment", *r["bond_investment"])
    cash = st.slider("cash", *r["cash"])

    st.subheader("Any investment properties?")

    number_of_investment_properties = st.number_input(
        "Number of investment properties?", 0, 6, 0
    )
    # st.slider("Number of investment properties?", 0, 6, 0)
    investment_properties: list[InvestmentProperty] = []

    for i in range(number_of_investment_properties):
        st.subheader(f"Property {i+1}")
        market_value = st.slider(f"market_value_{i+1}", *r["market_value"])
        mortgage_left = st.slider(f"mortgage_left_{i+1}", *r["mortgage_left"])
        mortgage_months = st.slider(f"mortgage_months_{i+1}", *r["mortgage_months"])
        mortgage_rate = st.slider(f"mortgage_rate_{i+1}", *r["mortgage_rate"])
        property_monthly_income = st.slider(
            f"property_monthly_income_{i+1}", *r["properties_monthly_income"]
        )
        annual_rent_increase_rate = st.slider(
            f"annual_rent_increase_rate_{i+1}", 0.01, 0.1, 0.01
        )

        i = InvestmentProperty(
            market_value=Decimal(market_value),
            mortgage_left=Decimal(mortgage_left),
            mortgage_months=mortgage_months,
            monthly_income=Decimal(property_monthly_income),
            mortgage_rate=Decimal(mortgage_rate),
            annual_rent_increase_rate=Decimal(annual_rent_increase_rate),
        )
        investment_properties.append(i)

    st.subheader("Configure parameters:")

    predefined_inflation_rate = st.selectbox(
        "Predefined inflation rate", ["fixed", "random", "historical"], index=0
    )
    if predefined_inflation_rate == "fixed":
        annual_inflation_rate = st.slider("inflation_rate", 0.0, 0.2, 0.04)
        inflation_gen = None
    elif predefined_inflation_rate == "random":
        inflation_gen = random_inflation_gen((1, 5))
        annual_inflation_rate = Decimal("0.0")
    elif predefined_inflation_rate == "historical":
        inflation_gen = inflation_from_file_gen(
            root_path / "data" / f"monthly_cpi_simulated_{currency_code}.csv",
            monthly=True,
        )
        annual_inflation_rate = Decimal("1.0")

    stock_return_rate = st.slider("return_rate_from_stock", 0.0, 0.2, 0.05)
    bonds_return_rate = st.slider("bonds_return_rate", 0.0, 0.2, 0.04)
    annual_income_increase_rate = st.slider(
        "annual_income_increase_rate", 0.0, 0.2, 0.03
    )
    annual_property_appreciation_rate = st.slider(
        "annual_property_appreciation_rate", 0.0, 0.1, 0.02
    )
    invest_cash_surplus = st.checkbox("Invest cash surplus", value=True)
    invest_cash_surplus_strategy = st.selectbox(
        "Invest cash surplus strategy", ["50-50", "60-40", "80-20"], index=1
    )

    invest_cash_threshold = st.slider(
        "Invest cash threshold", *r["invest_cash_threshold"]
    )

    return BaseSidebarAttrs(
        monthly_expenses=monthly_expenses,
        monthly_income=monthly_income,
        stock_investment=stock_investment,
        bond_investment=bond_investment,
        cash=cash,
        number_of_investment_properties=number_of_investment_properties,
        investment_properties=investment_properties,
        annual_inflation_rate=annual_inflation_rate,
        stock_return_rate=stock_return_rate,
        bonds_return_rate=bonds_return_rate,
        annual_income_increase_rate=annual_income_increase_rate,
        annual_property_appreciation_rate=annual_property_appreciation_rate,
        invest_cash_surplus=invest_cash_surplus,
        invest_cash_surplus_strategy=invest_cash_surplus_strategy,
        invest_cash_threshold=invest_cash_threshold,
        inflation_gen=inflation_gen,
    )
