import time

def age_seconds(timestamp):
    if timestamp is None:
        return None
    return max(0.0, time.time() - timestamp)

def is_fresh(timestamp, max_age):
    age = age_seconds(timestamp)
    return age is not None and age <= max_age

def data_status(timestamp, max_age):
    if timestamp is None:
        return "UNAVAILABLE"
    return "FRESH" if is_fresh(timestamp, max_age) else "STALE"
