import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime
from decimal import Decimal


project_root = Path.cwd()
src_path = project_root / "src"

sys.path.append(str(src_path))

from view.helpers import first_day_of_the_month
from view.sidebar import fire_sidebar
from finsim.simulations import FireSimulation, run_fire_simulation
from finsim.properties import InvestmentProperty


with st.sidebar:
    sidebarAttrs = fire_sidebar(project_root)


with st.container(border=False):

    st.title("When can I stop working?")

    """
    **This is a simple simulation of the FIRE (Financial Independence, Retire Early) concept.**
    The simulation will calculate how long you need to work to retire early and live from your investments, given you invest the surplus of the cash.

    Configure your current financial situation, that includes:
    - the monthly income, net of taxes, the monthly expenses
    - current investments, like: stocks, bonds, and cash.
    - investment properties, if you have any.
    - configure the expected return rates and inflation rate


    **The simulation does not take into account the taxes and pension, just your actual savings**

    """

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
        date=first_day_of_the_month(),
    )

    simulation, nmb_of_sims = run_fire_simulation(
        init,
        expected_number_of_months=sidebarAttrs.expected_number_of_months,
        inflation_rate_gen=sidebarAttrs.inflation_gen,
    )
    if len(simulation) < 2:
        st.error("No simulation data")
        st.stop()

    df = pd.DataFrame([s.to_dict() for s in simulation])
    # set date as an index
    df.set_index("date", inplace=True)

    first_month_with_zero_income = df[df["monthly_income"] == 0]
    if not first_month_with_zero_income.empty:
        years_to_retire = (
            first_month_with_zero_income.index[0].year - datetime.datetime.now().year
        )
        st.subheader(
            f"Retire in {years_to_retire} years, {first_month_with_zero_income.index[0].strftime('%B %Y')}"
        )
        "From that month your income will be zero, and you will live from your investments."
    else:
        st.subheader(
            "With current configuration, you will always need some kind of income stream."
        )

    st.subheader("FIRE curve - for how long you will need to work?")

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

    st.subheader("Month by month details")

    df
