FRESHNESS_STATES = {"VALID", "FRESH", "STALE", "PARTIALLY_AVAILABLE", "CROSS_VERIFIED", "UNVERIFIED", "UNAVAILABLE", "INVALID"}

EVIDENCE_TYPES = {"volume", "oi", "relative_strength", "spot_flow", "compression", "structure_break", "verified_catalyst", "liquidation_absorption"}

def evaluate_freshness(evidence, now=None):
    available = {k: v for k, v in (evidence or {}).items() if v is not None}
    if not available:
        return "UNAVAILABLE"
    stale = [k for k, v in available.items() if isinstance(v, dict) and v.get("state") == "STALE"]
    if stale:
        return "STALE"
    if len(available) < 1:
        return "PARTIALLY_AVAILABLE"
    return "FRESH"

def no_valid_signal(evidence):
    state = evaluate_freshness(evidence)
    return state in {"STALE", "UNAVAILABLE", "INVALID"}
