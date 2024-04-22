import sys
from pathlib import Path

project_root = Path.cwd()
src_path = project_root / "src"

sys.path.append(str(src_path))

import streamlit as st
import pandas as pd
import datetime
from decimal import Decimal
from streamlit.web.server.websocket_headers import _get_websocket_headers
from view.locale import set_locale, _
from view.helpers import first_day_of_the_month
from view.sidebar import (
    fire_sidebar,
    get_fire_sidebar_defaults,
    query_to_attrs,
    update_query_params,
)
from finsim.simulations import FireSimulation, run_fire_simulation
from finsim.properties import InvestmentProperty
from logging import getLogger

logger = getLogger(__name__)


try:
    headers = _get_websocket_headers()
except Exception as e:
    logger.error(f"Error while getting headers: {e}")
    headers = {}
locale = set_locale(headers)

if "query_params_read" not in st.session_state:
    b = get_fire_sidebar_defaults()
    defaults = query_to_attrs(b)
    st.session_state.query_params_read = True
    for k, v in defaults.__dict__.items():
        st.session_state[k] = v


with st.sidebar:
    "language: ", locale.lang
    sidebarAttrs = fire_sidebar(project_root)
    update_query_params(sidebarAttrs)


with st.container(border=False):

    def to_d(v: float) -> Decimal:
        return Decimal(str(v))

    with open(f"docs/firesim_intro_{locale.lang}.md", "r") as f:
        st.markdown(f.read())

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
        inflation_rate_gen=sidebarAttrs.inflation_gen(root_path=project_root),
        stock_gen=sidebarAttrs.stock_gen(root_path=project_root),
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
        fire_date = first_month_with_zero_income.index[0].strftime("%B %Y")

        retire_text = " ".join(
            [
                _("Retire in"),
                str(years_to_retire),
                _("years,"),
                fire_date,
            ]
        )

        st.subheader(retire_text)

        _(
            "From that month your income will be zero, and you will live from your investments."
        )
    else:
        st.subheader(
            _(
                "With current configuration, you will always need some kind of income stream."
            )
        )

    st.subheader(_("FIRE curve - for how long you will need to work?"))

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

    st.subheader(_("income_expenses_breakdown"))

    st.line_chart(df[["monthly_expenses", "monthly_income"]])

    st.subheader(_("Month by month details"))

    df
