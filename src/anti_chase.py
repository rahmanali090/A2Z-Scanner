def evaluate_anti_chase(change_percent, max_change_percent=5.0):
    change = abs(float(change_percent or 0))
    if change >= max_change_percent:
        return {
            "status": "BLOCK",
            "reason": "MOVE_TOO_EXTENDED",
            "change_percent": change,
            "threshold": max_change_percent,
        }
    return {
        "status": "PASS",
        "reason": "MOVE_WITHIN_LIMIT",
        "change_percent": change,
        "threshold": max_change_percent,
    }
