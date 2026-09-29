from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"
    UNSAFE = "UNSAFE"


HEALTH_COMPONENTS = (
    "BINANCE_WS",
    "BINANCE_REST",
    "BYBIT_WS",
    "BYBIT_REST",
    "DATABASE",
    "TELEGRAM",
    "CLOCK",
    "RATE_LIMIT",
    "DATA_FRESHNESS",
)


def can_confirm(status):
    return status == HealthStatus.HEALTHY


def overall_status(component_statuses):
    if not component_statuses:
        return HealthStatus.UNSAFE

    statuses = list(component_statuses.values())

    if any(status == HealthStatus.UNSAFE for status in statuses):
        return HealthStatus.UNSAFE

    if any(status == HealthStatus.RECOVERING for status in statuses):
        return HealthStatus.RECOVERING

    if any(status == HealthStatus.DEGRADED for status in statuses):
        return HealthStatus.DEGRADED

    return HealthStatus.HEALTHY
