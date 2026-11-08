import time

_recent_alerts = {}

def allow_alert(fingerprint, cooldown_seconds=300):
    now = time.time()
    last = _recent_alerts.get(fingerprint)
    if last is not None and now - last < cooldown_seconds:
        return False
    _recent_alerts[fingerprint] = now
    return True
