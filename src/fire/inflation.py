from decimal import Decimal
from typing import Generator
from random import randrange


def random_inflation_gen(range: tuple[int, int]) -> Generator[Decimal, None, None]:
    while True:
        random_between_range = randrange(range[0], range[1]) / 100
        yield Decimal(str(random_between_range))
