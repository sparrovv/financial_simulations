from dataclasses import dataclass
import datetime
from decimal import Decimal
from pathlib import Path
from typing import Generator

from finsim.inflation import inflation_from_file_gen
from finsim.properties import InvestmentProperty


@dataclass
class BaseSidebarAttrs:
    currency_code: str
    monthly_income: float
    monthly_expenses: float
    stock_investment: float
    bond_investment: float
    cash: float
    number_of_investment_properties: int
    investment_properties: list[InvestmentProperty]
    annual_inflation_rate: float
    stock_return_rate: float
    bonds_return_rate: float
    annual_income_increase_rate: float
    annual_property_appreciation_rate: float
    invest_cash_surplus: bool
    invest_cash_surplus_strategy: str
    invest_cash_threshold: float
    inflation_type_calc: str

    def inflation_gen(self, root_path: Path) -> Generator[Decimal, None, None]:
        gen = None
        if self.inflation_type_calc == "simulated":
            gen = inflation_from_file_gen(
                root_path / "data" / f"monthly_cpi_simulated_{self.currency_code}.csv",
                monthly=True,
            )

        return gen


@dataclass
class FireSidebarAttrs(BaseSidebarAttrs):
    current_age: int
    expected_age: int
    date_of_death: datetime.datetime
    expected_number_of_months: int

    def __init__(self, **kwargs):
        for k in self.__dataclass_fields__:
            setattr(self, k, None)

        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass
class SimpleSimSidebarAttrs(BaseSidebarAttrs):
    years: int
