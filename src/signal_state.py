ALLOWED_TRANSITIONS = {
    "DETECTED": {"DEVELOPING", "CANDIDATE", "INVALIDATED", "EXPIRED"},
    "DEVELOPING": {"CANDIDATE", "CONFIRMED", "INVALIDATED", "EXPIRED"},
    "CANDIDATE": {"CONFIRMED", "DEVELOPING", "INVALIDATED", "EXPIRED"},
    "CONFIRMED": {"MONITORING", "UPGRADED", "DOWNGRADED", "INVALIDATED", "EXPIRED"},
    "MONITORING": {"UPGRADED", "DOWNGRADED", "INVALIDATED", "EXPIRED"},
    "UPGRADED": {"MONITORING", "DOWNGRADED", "INVALIDATED", "EXPIRED"},
    "DOWNGRADED": {"MONITORING", "UPGRADED", "INVALIDATED", "EXPIRED"},
    "INVALIDATED": set(),
    "EXPIRED": set(),
}

VALID_STATES = {"DETECTED", "DEVELOPING", "CANDIDATE", "CONFIRMED", "MONITORING", "UPGRADED", "DOWNGRADED", "INVALIDATED", "EXPIRED"}

def transition(current, new):
    if current not in VALID_STATES:
        raise ValueError(f"Invalid state: {current}")
    if new not in VALID_STATES:
        raise ValueError(f"Invalid state: {new}")
    if new not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid transition: {current} -> {new}")
    return new

def is_terminal(state):
    return state in {"INVALIDATED", "EXPIRED"}
