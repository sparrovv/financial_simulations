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
