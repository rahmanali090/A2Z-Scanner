from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MarketSnapshot:
    symbol: str
    price: Optional[float] = None
    volume: Optional[float] = None
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    timestamp: Optional[float] = None

@dataclass
class Signal:
    signal_id: str
    symbol: str
    state: str
    confidence: Optional[float] = None
    reason: str = ""
    created_at: float = 0.0
    metadata: dict = field(default_factory=dict)
