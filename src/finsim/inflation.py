from decimal import Decimal
from typing import Generator
from random import randrange


def random_inflation_gen(range: tuple[int, int]) -> Generator[Decimal, None, None]:
    while True:
        random_between_range = randrange(range[0], range[1]) / 100
        yield Decimal(str(random_between_range))


def rate_from_file_gen(
    rate_path: str, monthly: bool = False
) -> Generator[Decimal, None, None]:
    return inflation_from_file_gen(rate_path, monthly)


def inflation_from_file_gen(
    inflation_path: str, monthly: bool = False
) -> Generator[Decimal, None, None]:
    """
    the file is a CSV with the first column being the date and the second column being the inflation rate.

    This function will load the file and yield the inflation rate,
    once the file finish it will start again from the beginning.

    If monthly arg is True, it will divide the inflation rate by 12 to get the monthly inflation rate and
    return it 12 times.
    """

    with open(inflation_path, "r") as file:
        data = file.readlines()
        assert data[0].strip() == "date,value"
        while True:
            for line in data:
                if line.strip() == "date,value":
                    continue
                date, inflation_rate = map(
                    lambda x: x.strip(),
                    line.split(","),
                )

                if monthly:
                    yield Decimal(inflation_rate)
                else:
                    for _ in range(12):
                        yield round(Decimal(inflation_rate) / Decimal("12"), 3)

            file.seek(0)
