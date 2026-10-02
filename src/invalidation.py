def evaluate_invalidation(direction, price, reference_price, invalidation_percent=1.0):
    price = float(price)
    reference_price = float(reference_price)
    distance = abs((price - reference_price) / reference_price * 100)

    if direction == "BULLISH" and price < reference_price * (1 - invalidation_percent / 100):
        status = "INVALIDATED"
    elif direction == "BEARISH" and price > reference_price * (1 + invalidation_percent / 100):
        status = "INVALIDATED"
    else:
        status = "VALID"

    return {
        "status": status,
        "direction": direction,
        "price": price,
        "reference_price": reference_price,
        "distance_percent": distance,
        "threshold_percent": invalidation_percent,
    }
