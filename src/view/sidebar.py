from dataclasses import replace, asdict
from pathlib import Path
import streamlit as st
import json
import datetime
from datetime import timedelta
from decimal import Decimal
from finsim.properties import InvestmentProperty
from view.conf import get_ranges
from view.sidebar_conf import BaseSidebarAttrs, FireSidebarAttrs, SimpleSimSidebarAttrs
from urllib.parse import quote_plus, unquote_plus
import logging

logger = logging.getLogger(__name__)


class JEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def update_query_params(attrs: BaseSidebarAttrs) -> None:
    # convert dataclass attrs to json
    json_str = json.dumps(asdict(attrs), cls=JEncoder)
    encoded = quote_plus(json_str)

    st.query_params["props"] = encoded


def query_to_attrs(defaults: BaseSidebarAttrs) -> BaseSidebarAttrs:
    accu = {}
    probablyJson = st.query_params.get("props", None)

    try:
        # this can fail as people can tamper with the query params
        if probablyJson:
            decoded = unquote_plus(probablyJson)
            accu = json.loads(decoded)

        return replace(defaults, **accu)

    except Exception as e:
        logger.warn("Failed to parse query params")
        logger.warn(e)
        return defaults


def simple_sim_sidebar(root_path: Path) -> SimpleSimSidebarAttrs:
    currency_code: str = st.selectbox(
        "Select currency code", ["PLN", "USD", "EUR"], index=0, key="currency_code"
    )  # type: ignore

    years = st.slider("How many years to simulate?", 1, 100, key="years")
    f"Simulating for {years} years"

    base = _shared(root_path, currency_code)

    return SimpleSimSidebarAttrs(
        years=years,
        **base.__dict__,
    )


def get_simple_sidebar_defaults() -> FireSidebarAttrs:
    return SimpleSimSidebarAttrs(
        currency_code="PLN",
        years=15,
        monthly_income=Decimal("10_000"),
        monthly_expenses=Decimal("8_000"),
        stock_investment=Decimal("0"),
        bond_investment=Decimal("0"),
        cash=Decimal("10_000"),
        number_of_investment_properties=0,
        investment_properties=[],
        annual_inflation_rate=Decimal("0.02"),
        stock_return_rate=Decimal("0.05"),
        bonds_return_rate=Decimal("0.02"),
        annual_income_increase_rate=Decimal("0.02"),
        annual_property_appreciation_rate=Decimal("0.02"),
        invest_cash_surplus=True,
        invest_cash_surplus_strategy="60-40",
        invest_cash_threshold=Decimal("50000"),
        inflation_type_calc="fixed",
    )


def get_fire_sidebar_defaults() -> FireSidebarAttrs:
    expected_age = 80
    return FireSidebarAttrs(
        currency_code="PLN",
        current_age=38,
        expected_age=expected_age,
        date_of_death=datetime.datetime.now() + timedelta(days=expected_age * 365),
        expected_number_of_months=expected_age * 12,
        monthly_income=Decimal("10_000"),
        monthly_expenses=Decimal("8_000"),
        stock_investment=Decimal("0"),
        bond_investment=Decimal("0"),
        cash=Decimal("10_000"),
        number_of_investment_properties=0,
        investment_properties=[],
        annual_inflation_rate=Decimal("0.02"),
        stock_return_rate=Decimal("0.05"),
        bonds_return_rate=Decimal("0.02"),
        annual_income_increase_rate=Decimal("0.02"),
        annual_property_appreciation_rate=Decimal("0.02"),
        invest_cash_surplus=True,
        invest_cash_surplus_strategy="60-40",
        invest_cash_threshold=Decimal("50000"),
        inflation_type_calc="fixed",
    )


def fire_sidebar(root_path: Path) -> FireSidebarAttrs:
    currency_code: str = st.selectbox(
        "Select currency code", ["PLN", "USD", "EUR"], index=0, key="currency_code"
    )  # type: ignore

    current_age = st.slider("How old are you?", 0, 100, key="current_age")
    expected_age = st.slider(
        "Life expectancy?",
        0,
        100,
        key="expected_age",
    )
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


def _shared(root_path: Path, currency_code: str) -> BaseSidebarAttrs:
    r = get_ranges(currency_code)
    st.subheader("Provide monthly income and expenses:")
    monthly_income = st.number_input("income", 0, key="monthly_income", step=500)
    monthly_expenses = st.number_input(
        "monthly_expenses", 0, key="monthly_expenses", step=500
    )

    st.subheader("Provide basic savings and expenses information:")
    stock_investment = st.number_input(
        "stock_investment", 0, key="stock_investment", step=1000
    )
    bond_investment = st.number_input("bond_investment", 0, key="bond_investment")
    cash = st.number_input("cash", 0, key="cash", step=1000)

    st.subheader("Any investment properties?")

    number_of_investment_properties = st.number_input(
        "Number of investment properties?", 0, key="number_of_investment_properties"
    )
    investment_properties: list[InvestmentProperty] = []

    for i in range(number_of_investment_properties):
        st.subheader(f"Property {i+1}")
        market_value = st.number_input(f"market_value_{i+1}", 0)
        mortgage_left = st.number_input(f"mortgage_left_{i+1}", 0)
        mortgage_months = st.number_input(f"mortgage_months_{i+1}", 0)
        mortgage_rate = st.slider(f"mortgage_rate_{i+1}", *r["mortgage_rate"])
        property_monthly_income = st.number_input(f"property_monthly_income_{i+1}", 0)
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

    inflation_type_calc = st.selectbox(
        "Predefined inflation rate",
        ["fixed", "simulated"],
        index=0,
        key="inflation_type_calc",
    )

    annual_inflation_rate = Decimal("0.02")
    if inflation_type_calc == "fixed":
        annual_inflation_rate = st.slider(
            "inflation_rate", 0.0, 0.2, key="annual_inflation_rate"
        )

    stock_return_rate = st.slider(
        "return_rate_from_stock", 0.0, 0.2, key="stock_return_rate"
    )
    bonds_return_rate = st.slider(
        "bonds_return_rate", 0.0, 0.2, key="bonds_return_rate"
    )
    annual_income_increase_rate = st.slider(
        "annual_income_increase_rate", 0.0, 0.2, key="annual_income_increase_rate"
    )
    annual_property_appreciation_rate = st.slider(
        "annual_property_appreciation_rate",
        0.0,
        0.1,
        key="annual_property_appreciation_rate",
    )
    invest_cash_surplus = st.checkbox(
        "Invest cash surplus", value=True, key="invest_cash_surplus"
    )
    invest_cash_surplus_strategy = st.selectbox(
        "Invest cash surplus strategy",
        ["50-50", "60-40", "80-20"],
        index=1,
        key="invest_cash_surplus_strategy",
    )

    invest_cash_threshold = st.slider(
        "Invest cash threshold",
        *r["invest_cash_threshold"],
        key="invest_cash_threshold",
    )

    return BaseSidebarAttrs(
        currency_code=currency_code,
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
        inflation_type_calc=inflation_type_calc,
    )