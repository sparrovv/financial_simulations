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
from view.conf import get_ranges
from view.sidebar import simple_sim_sidebar

with st.sidebar:
    sidebarAttrs = simple_sim_sidebar(project_root)


with st.container(border=False):

    st.title("Simulate your savings and wealth growth over time")

    def to_d(v: float) -> Decimal:
        return Decimal(str(v))

    init = FireSimulation(
        stock_investments=to_d(sidebarAttrs.stock_investment),
        bonds_investments=to_d(sidebarAttrs.bond_investment),
        cash=to_d(sidebarAttrs.cash),
        monthly_income=to_d(sidebarAttrs.monthly_income),
        monthly_expenses=to_d(sidebarAttrs.monthly_expenses),
        investment_properties=[
            InvestmentProperty(
                market_value=to_d(i.market_value),
                mortgage_left=to_d(i.mortgage_left),
                mortgage_months=i.mortgage_months,
                monthly_income=to_d(i.monthly_income),
                mortgage_rate=to_d(i.mortgage_rate),
            )
            for i in sidebarAttrs.investment_properties
        ],
        stock_return_rate=to_d(sidebarAttrs.stock_return_rate),
        bonds_return_rate=to_d(sidebarAttrs.bonds_return_rate),
        annual_inflation_rate=to_d(sidebarAttrs.annual_inflation_rate),
        annual_income_increase_rate=to_d(sidebarAttrs.annual_income_increase_rate),
        annual_property_appreciation_rate=to_d(
            sidebarAttrs.annual_property_appreciation_rate
        ),
        invest_cash_surplus=sidebarAttrs.invest_cash_surplus,
        invest_cash_threshold=to_d(sidebarAttrs.invest_cash_threshold),
        invest_cash_surplus_strategy=sidebarAttrs.invest_cash_surplus_strategy,
        date=datetime.datetime.fromisoformat("2024-03-01"),
    )

    # simulate for next X years
    simulation = run_simulation(
        init, sidebarAttrs.years * 12, inflation_rate_gen=sidebarAttrs.inflation_gen
    )

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
