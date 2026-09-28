VALID_STATES = {"DETECTED", "DEVELOPING", "CANDIDATE", "CONFIRMED", "MONITORING", "UPGRADED", "DOWNGRADED", "INVALIDATED", "EXPIRED"}

def transition(current, new):
    if new not in VALID_STATES:
        raise ValueError(f"Invalid state: {new}")
    return new

def is_terminal(state):
    return state in {"INVALIDATED", "EXPIRED"}
