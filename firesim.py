import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
from decimal import Decimal


project_root = Path.cwd()
src_path = project_root / "src"

sys.path.append(str(src_path))

from fire.simulations import FireSimulation, run_fire_simulation, InvestmentProperty


with st.sidebar:
    current_age = st.slider("How old are you?", 0, 100, 38)
    expected_age = st.slider("Life expectancy?", 0, 100, 85)
    years = expected_age - current_age
    f"Simulating for {years} years"

    date_of_death = datetime.datetime.now() + timedelta(days=years * 365)
    expected_number_of_months = years * 12

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
        mortgage_rate = st.slider(f"mortgage_rate_{i+1}", 0.1, 20.0, 7.66)
        property_monthly_income = st.slider(
            f"property_monthly_income_{i+1}", 0, 10_000, 2500
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
        "annual_income_increase_rate", 0.0, 0.2, 0.03
    )
    invest_cash_surplus = st.checkbox("Invest cash surplus", value=True)
    invest_cash_surplus_strategy = st.selectbox(
        "Invest cash surplus strategy", ["50-50", "60-40", "80-20"], index=1
    )

    invest_cash_threshold = st.slider("Invest cash threshold", 0, 100_000, 50_000)


with st.container(border=False):

    st.title("When can I stop working? FIRE simulation!")

    """
    **This is a simple simulation of the FIRE (Financial Independence, Retire Early) concept.**

    Configure your current financial situation.
    What's the monthly income and expenses. 
    How much do you have in stocks, bonds, and cash.

    Add any investment properties.

    """

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
        invest_cash_surplus_strategy=invest_cash_surplus_strategy,
        date=datetime.datetime.fromisoformat("2024-03-01"),
    )

    # simulate for next X years
    # simulation = run_simulation(init, years * 12)
    simulation, nmb_of_sims = run_fire_simulation(
        init, expected_number_of_months=expected_number_of_months
    )
    if len(simulation) < 2:
        st.error("No simulation data")
        st.stop()

    df = pd.DataFrame([s.to_dict() for s in simulation])
    # set date as an index
    df.set_index("date", inplace=True)

    first_month_with_zero_income = df[df["monthly_income"] == 0]
    # check if there is a month with zero income
    if not first_month_with_zero_income.empty:
        years_to_retire = (
            first_month_with_zero_income.index[0].year - datetime.datetime.now().year
        )
        st.subheader(
            f"Retire in {years_to_retire} years, {first_month_with_zero_income.index[0].strftime('%B %Y')}"
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

    st.subheader("Granular data")

    df

    # st.scatter_chart(df[["monthly_expenses", "monthly_income"]])
