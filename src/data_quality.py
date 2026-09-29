from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).timestamp()


def age_seconds(timestamp, now=None):
    if timestamp is None:
        return None

    if now is None:
        now = utc_now()

    return max(0.0, now - timestamp)


def is_fresh(timestamp, max_age, now=None):
    age = age_seconds(timestamp, now)
    return age is not None and age <= max_age


def data_status(timestamp, max_age, now=None):
    if timestamp is None:
        return "UNAVAILABLE"

    return "FRESH" if is_fresh(timestamp, max_age, now) else "STALE"


def timing_status(source_timestamp, receipt_timestamp, processing_timestamp,
                  decision_timestamp):
    timestamps = {
        "SOURCE": source_timestamp,
        "RECEIPT": receipt_timestamp,
        "PROCESSING": processing_timestamp,
        "DECISION": decision_timestamp,
    }

    if any(value is None for value in timestamps.values()):
        return "DEGRADED"

    if (
        receipt_timestamp < source_timestamp
        or processing_timestamp < receipt_timestamp
        or decision_timestamp < processing_timestamp
    ):
        return "DEGRADED"

    return "OK"
