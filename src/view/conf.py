ranges = {
    "USD": {
        "monthly_income": (0, 20_000),
        "monthly_expenses": (0, 20_000),
        "stock_investment": (0, 1_000_000),
        "bond_investment": (0, 1_000_000),
        "cash": (0, 100_000),
        "invest_cash_threshold": (0, 50_000),
        "market_value": (0, 3_000_000),
        "mortgage_left": (0, 3_000_000),
        "mortgage_months": (0, 360),
        "mortgage_rate": (0.1, 20.0),
        "properties_monthly_income": (0, 5_000),
    },
    "PLN": {
        "monthly_income": (0, 80_000),
        "monthly_expenses": (0, 80_000),
        "stock_investment": (0, 2_000_000),
        "bond_investment": (0, 2_000_000),
        "cash": (0, 2_000_000),
        "invest_cash_threshold": (0, 100_000),
        "market_value": (0, 2_000_000),
        "mortgage_left": (0, 2_000_000),
        "mortgage_months": (0, 360),
        "mortgage_rate": (0.1, 20.0),
        "properties_monthly_income": (0, 10_000),
    },
    "EUR": {
        "monthly_income": (0, 20_000),
        "monthly_expenses": (0, 20_000),
        "stock_investment": (0, 500_000),
        "bond_investment": (0, 500_000),
        "cash": (0, 500_000),
        "invest_cash_threshold": (0, 50_000),
        "market_value": (0, 3_000_000),
        "mortgage_left": (0, 3_000_000),
        "mortgage_months": (0, 360),
        "mortgage_rate": (0.1, 20.0),
        "properties_monthly_income": (0, 5_000),
    },
}


def get_ranges(currency_code: str) -> dict[str, tuple]:
    return ranges[currency_code]
