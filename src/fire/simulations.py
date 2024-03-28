from dataclasses import dataclass, asdict
from datetime import date


@dataclass
class FireSimulation:
    stock_investments: float
    bonds_investments: float
    properties_market_value: float
    properties_monthly_income: float
    # monthly_mort
    # combined_mortgage_left: float
    # combined_mortgage_rate: float
    # combined_mortgage_months: int

    cash: float
    return_rate_from_investment: float
    monthly_expenses: float
    monthly_income: float
    start_date: date

    def to_dict(self):
        return asdict(self)


def simulate_next(prev: FireSimulation) -> FireSimulation:
    # add one month to the start date
    next_month = prev.start_date.replace(month=prev.start_date.month + 1)

    # total expenses
    total_monthly_expenses = prev.monthly_expenses

    # total income
    total_monthly_cash = (
        prev.cash + prev.monthly_income + prev.properties_monthly_income
    )
    prev.cash += prev.monthly_income + prev.properties_monthly_income

    new_bonds_investments = prev.bonds_investments
    new_stock_investments = prev.stock_investments

    if total_monthly_cash > total_monthly_expenses:
        new_cash = total_monthly_cash - total_monthly_expenses
    elif (total_monthly_cash + prev.stock_investments) > total_monthly_expenses:
        new_cash = 0
        cash_needed = total_monthly_expenses - prev.cash
        new_stock_investments = prev.stock_investments - cash_needed
    elif (
        total_monthly_cash + prev.stock_investments + prev.bonds_investments
    ) > total_monthly_expenses:
        new_cash = 0
        cash_needed = (
            total_monthly_expenses - total_monthly_cash - prev.stock_investments
        )
        new_stock_investments = 0
        new_bonds_investments = prev.bonds_investments - cash_needed
    else:
        cash_needed = (
            total_monthly_expenses
            - total_monthly_cash
            - prev.stock_investments
            - prev.bonds_investments
        )
        new_stock_investments = 0
        new_bonds_investments = 0
        new_cash = -cash_needed

    return FireSimulation(
        stock_investments=new_stock_investments,
        bonds_investments=new_bonds_investments,
        properties_market_value=prev.properties_market_value,
        properties_monthly_income=prev.properties_monthly_income,
        # combined_mortgage_left=prev.combined_mortgage_left,
        # combined_mortgage_rate=prev.combined_mortgage_rate,
        # combined_mortgage_months=prev.combined_mortgage_months,
        cash=new_cash,
        return_rate_from_investment=prev.return_rate_from_investment,
        monthly_expenses=prev.monthly_expenses,
        monthly_income=prev.monthly_income,
        start_date=next_month,
    )


def calculate_monthly_mortgage_payment(
    mortgage_left: float, mortgage_rate: float, mortgage_months: int
) -> tuple[float, float]:
    """to calculate the monthly mortgage payment, we need to use the formula:
    mortgage_payment = P[r(1+r)^n]/[(1+r)^n - 1]
    where:
    P = principal loan amount
    r = monthly interest rate
    n = number of months
    """
    if mortgage_months == 0:
        return 0, 0

    r = mortgage_rate / 12

    pmt = mortgage_left * (
        (r * ((1 + r) ** mortgage_months)) / (((1 + r) ** mortgage_months) - 1)
    )

    monthly_interest = mortgage_left * r

    return pmt, monthly_interest


def calculate_mortgage(
    principal_amount: float, mortgage_rate: float, mortgage_months: int
) -> tuple[float, float]:
    # Convert annual rate to a decimal and then divide by 12 for a monthly rate
    r = mortgage_rate / 12

    # Monthly Mortgage Payment Calculation
    if r != 0:
        # If there's an actual interest rate apply full formula
        M = (
            principal_amount
            * (r * ((1 + r) ** mortgage_months))
            / (((1 + r) ** mortgage_months) - 1)
        )

        # Initial Month Interest Calculation
        initial_interest = principal_amount * r

        return M, initial_interest
    else:
        return principal_amount / mortgage_months, 0
