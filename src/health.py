from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"
    UNSAFE = "UNSAFE"

def can_confirm(status):
    return status == HealthStatus.HEALTHY
