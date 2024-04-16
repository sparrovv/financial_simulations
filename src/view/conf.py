ranges = {
    "USD": {
        "monthly_income": (0, 20_000, 5_000),
        "monthly_expenses": (0, 20_000, 4_000),
        "stock_investment": (0, 1_000_000, 0),
        "bond_investment": (0, 1_000_000, 0),
        "cash": (0, 100_000, 10_000),
        "invest_cash_threshold": (0, 50_000, 20_000),
        "market_value": (0, 3_000_000, 0),
        "mortgage_left": (0, 3_000_000, 0),
        "mortgage_months": (0, 360, 0),
        "mortgage_rate": (0.1, 20.0, 0.0),
        "properties_monthly_income": (0, 5_000, 0),
    },
    "PLN": {
        "monthly_income": (0, 80_000, 12_000),
        "monthly_expenses": (0, 80_000, 8_000),
        "stock_investment": (0, 2_000_000, 0),
        "bond_investment": (0, 2_000_000, 0),
        "cash": (0, 2_000_000, 50_000),
        "invest_cash_threshold": (0, 100_000, 50_000),
        "market_value": (0, 2_000_000, 0),
        "mortgage_left": (0, 2_000_000, 0),
        "mortgage_months": (0, 360, 0),
        "mortgage_rate": (0.1, 20.0, 0.0),
        "properties_monthly_income": (0, 10_000, 0),
    },
    "EUR": {
        "monthly_income": (0, 20_000, 5_000),
        "monthly_expenses": (0, 20_000, 4_000),
        "stock_investment": (0, 500_000, 0),
        "bond_investment": (0, 500_000, 0),
        "cash": (0, 500_000),
        "invest_cash_threshold": (0, 50_000, 20_000),
        "market_value": (0, 3_000_000, 0),
        "mortgage_left": (0, 3_000_000, 0),
        "mortgage_months": (0, 360, 0),
        "mortgage_rate": (0.1, 20.0, 0.0),
        "properties_monthly_income": (0, 5_000, 0),
    },
}


def get_ranges(currency_code: str):
    return ranges[currency_code]
