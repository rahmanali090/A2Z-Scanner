def calculate_risk_reward(entry, stop, target):
    entry = float(entry)
    stop = float(stop)
    target = float(target)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    ratio = (reward / risk) if risk else None
    return {
        "entry": entry,
        "stop": stop,
        "target": target,
        "risk": risk,
        "reward": reward,
        "risk_reward": ratio,
    }
