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

from fire.simulations import FireSimulation, run_simulation, InvestmentProperty

st.title("Simulate your savings and wealth growth over time")

years = st.slider("how_many_years_to_simulate", 0, 30, 15)

st.subheader("Provide monthly income and expenses:")
monthly_income = st.slider("income", 0, 100_000, 10_000)
monthly_expenses = st.slider("monthly_expenses", 0, 100_000, 10_000)

st.subheader("Provide basic savings and expenses information:")
stock_investment = st.slider("stock_investment", 0, 10_00_000, 100_000)
bond_investment = st.slider("bond_investment", 0, 10_00_000, 100_000)
cash = st.slider("cash", 0, 10_00_000, 50_000)

st.subheader("Any investment properties?")

number_of_investment_properties = st.number_input(
    "Number of investment properties?", 0, 6, 0
)
# st.slider("Number of investment properties?", 0, 6, 0)
investment_properties: list[InvestmentProperty] = []

for i in range(number_of_investment_properties):
    st.subheader(f"Property {i+1}")
    market_value = st.slider(f"market_value_{i+1}", 0, 3_000_000, 500_000)
    mortgage_left = st.slider(f"mortgage_left_{i+1}", 0, 3_000_000, 500_000)
    mortgage_months = st.slider(f"mortgage_months_{i+1}", 0, 360, 360)
    property_monthly_income = st.slider(
        f"property_monthly_income_{i+1}", 0, 10_000, 2500
    )
    mortgage_rate = st.slider(f"mortgage_rate_{i+1}", 0.1, 20.0, 7.66)

    i = InvestmentProperty(
        market_value=Decimal(market_value),
        mortgage_left=Decimal(mortgage_left),
        mortgage_months=mortgage_months,
        monthly_income=Decimal(property_monthly_income),
        mortgage_rate=Decimal(mortgage_rate),
    )
    investment_properties.append(i)


st.subheader("Configure parameters:")

annual_inflation_rate = st.slider("inflation_rate", 0.0, 0.2, 0.04)
stock_return_rate = st.slider("return_rate_from_stock", 0.0, 0.2, 0.05)
bonds_return_rate = st.slider("bonds_return_rate", 0.0, 0.2, 0.04)
annual_income_increase_rate = st.slider("annual_income_increase_rate", 0.0, 0.2, 0.03)
invest_cash_surplus = st.checkbox("Invest cash surplus", value=True)
invest_cash_threshold = st.slider("Invest cash threshold", 0, 100_000, 50_000)


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
        )
        for i in investment_properties
    ],
    stock_return_rate=to_d(stock_return_rate),
    bonds_return_rate=to_d(bonds_return_rate),
    annual_inflation_rate=to_d(annual_inflation_rate),
    annual_income_increase_rate=to_d(annual_income_increase_rate),
    annual_property_appreciation_rate=to_d("0.02"),
    invest_cash_surplus=invest_cash_surplus,
    invest_cash_threshold=to_d(invest_cash_threshold),
    invest_cash_surplus_strategy="80-20",
    date=datetime.datetime.fromisoformat("2024-03-01"),
)

# simulate for next X years
simulation = run_simulation(init, years * 12)

df = pd.DataFrame([s.to_dict() for s in simulation])

st.subheader("Granular data")

df

st.subheader("The wealth graph")

fig = px.bar(
    df,
    x=df["date"],
    y=[
        "properties_net_cash_value",
        "stock_investments",
        "bonds_investments",
        "cash",
    ],
    title="Wealth over time",
)
# fig.add_scatter(
#     x=df["date"], y=df["monthly_expenses"], mode="lines", name="Monthly expenses"
# )
# fig.add_scatter(
#     x=df["date"], y=df["monthly_income"], mode="lines", name="Monthly income"
# )
# fig.add_scatter(
#     x=df["date"],
#     y=df["wealth_inc_properties"],
#     mode="lines",
#     name="Wealth with net properties",
# )

fig

st.subheader("Investment properties")
