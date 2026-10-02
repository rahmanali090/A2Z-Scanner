import time

def health_check(last_success_timestamp, max_age_seconds=300):
    age = time.time() - float(last_success_timestamp)
    return {
        "status": "HEALTHY" if age <= max_age_seconds else "STALE",
        "age_seconds": age,
        "max_age_seconds": max_age_seconds,
    }
