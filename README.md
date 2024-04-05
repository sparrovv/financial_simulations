# Financial simulations

This project started with these two questions:

- If I stop working, how long can my savings last?
- How much can I save over the next couple of years given my current income, expenses, and wealth?

It's a simple simulation, but it can be quite useful.

It takes into account:

- Stock savings (assuming global EFT) and the adjustable annual return rate
- Bonds savings and the adjustable annual return rate
- Cash savings 
- Inflation rate (adjustable, but static)
- Monthly Income and expenses
- Investments in real estate, mortgage, and the income from renting
- Reinvestment of the spare cash into stocks and bonds with the adjustable ratio
- When there's no more cash, it sells stocks, bonds and then real estate to cover the expenses

It doesn't take into account:

- Taxes 
- Other sources of income
- And probably many more things

Things to do:

- Simulate the stock market rate of returns based on some historical data
- Simulate the inflation rate based on some historical data
- Add more visualizations

## streamlit

https://finsim.streamlit.app/

## tests

```
pipx install nox

nox
```
