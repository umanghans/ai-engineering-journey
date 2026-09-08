TAX_RATE = 0.06


def calculate_total(price: float, quantity: int = 1) -> float:
    subtotal = price * quantity
    tax = subtotal * TAX_RATE
    return subtotal + tax