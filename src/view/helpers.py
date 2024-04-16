import datetime


def first_day_of_the_month():
    return datetime.datetime.now().replace(day=1)
