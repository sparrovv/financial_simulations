import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from decimal import Decimal

project_root = Path.cwd()
src_path = project_root / "src"

sys.path.append(str(src_path))

from fire.properties import InvestmentProperty
from fire.simulations import FireSimulation, run_simulation
from conf import get_ranges

with st.sidebar:
    currency_code = st.selectbox("Select currency code", ["USD", "PLN", "EUR"], index=0)
    r = get_ranges(currency_code)
    years = st.slider("How many years to simulate?", 1, 100, 20)

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

    annual_inflation_rate = st.slider("inflation_rate", 0.0, 0.2, 0.04)
    stock_return_rate = st.slider("return_rate_from_stock", 0.0, 0.2, 0.05)
    bonds_return_rate = st.slider("bonds_return_rate", 0.0, 0.2, 0.04)
    annual_income_increase_rate = st.slider(
        "annual_income_increase_rate", 0.0, 0.2, 0.01
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


with st.container(border=False):

    st.title("Simulate your savings and wealth growth over time")

    def to_d(v: float) -> Decimal:
        return Decimal(str(v))

    init = FireSimulation(
        stock_investments=to_d(stock_investment),
        bonds_investments=to_d(bond_investment),
        cash=to_d(cash),
        monthly_income=to_d(monthly_income),
        monthly_expenses=to_d(monthly_expenses),
        investment_properties=[
            InvestmentProperty(
                market_value=to_d(i.market_value),
                mortgage_left=to_d(i.mortgage_left),
                mortgage_months=i.mortgage_months,
                monthly_income=to_d(i.monthly_income),
                mortgage_rate=to_d(i.mortgage_rate),
                annual_rent_increase_rate=to_d(i.annual_rent_increase_rate),
            )
            for i in investment_properties
        ],
        stock_return_rate=to_d(stock_return_rate),
        bonds_return_rate=to_d(bonds_return_rate),
        annual_inflation_rate=to_d(annual_inflation_rate),
        annual_income_increase_rate=to_d(annual_income_increase_rate),
        annual_property_appreciation_rate=to_d(annual_property_appreciation_rate),
        invest_cash_surplus=invest_cash_surplus,
        invest_cash_threshold=to_d(invest_cash_threshold),
        invest_cash_surplus_strategy=invest_cash_surplus_strategy,
        date=datetime.datetime.fromisoformat("2024-03-01"),
    )

    # simulate for next X years
    simulation = run_simulation(init, years * 12)

    df = pd.DataFrame([s.to_dict() for s in simulation])
    # set date as an index
    df.set_index("date", inplace=True)

    st.subheader("The wealth graph")

    st.bar_chart(
        df[
            [
                "properties_net_cash_value",
                "stock_investments",
                "bonds_investments",
                "cash",
            ]
        ]
    )

    st.subheader("Income and expenses")
    st.scatter_chart(df[["monthly_expenses", "monthly_income"]])

    st.subheader("Granular data")

    df
