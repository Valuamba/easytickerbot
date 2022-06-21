def get_float_payment_amount(amount):
    return "{:.2f}".format(round(amount, 2))


def get_integer_big_payment_amount(amount):
    return int(round(amount, 2) * 100)
