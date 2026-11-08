import json
import sqlite3
import time
from src.binance_data import get_klines

DB_PATH = "a2z_scanner.db"
HORIZON = 4 * 60 * 60


def evaluate_signal(event_timestamp, data):
    symbol=data["symbol"]
    direction=data["direction"]
    entry=float(data["entry"])
    stop_loss=float(data["stop_loss"])
    tp1=float(data["tp1"])
    if direction not in ("LONG","SHORT"):
        return "AMBIGUOUS",None,{"reason":"invalid_direction"}
    start=float(event_timestamp); end=start+HORIZON; now=time.time()
    if now<end:
        return "PENDING",None,{"reason":"horizon_not_complete","horizon_seconds":HORIZON,"remaining_seconds":end-now}
    candles=get_klines(symbol,"5m",1000)
    candles=[c for c in candles if start<=float(c[0])/1000.0<=end and float(c[6])/1000.0<=now]
    if not candles:
        return "EXPIRED",None,{"reason":"no_completed_candles_in_horizon","horizon_seconds":HORIZON}
    candles.sort(key=lambda c:float(c[0]))
    for candle in candles:
        candle_time=float(candle[0])/1000.0; high=float(candle[2]); low=float(candle[3])
        if direction=="LONG": tp_hit=high>=tp1; sl_hit=low<=stop_loss
        else: tp_hit=low<=tp1; sl_hit=high>=stop_loss
        if tp_hit and sl_hit: return "AMBIGUOUS",candle_time,{"reason":"same_5m_candle_tp1_and_sl","candle_open":candle[0],"high":high,"low":low}
        if tp_hit: return "WIN",candle_time,{"reason":"tp1_before_sl","candle_open":candle[0],"high":high,"low":low}
        if sl_hit: return "LOSS",candle_time,{"reason":"sl_before_tp1","candle_open":candle[0],"high":high,"low":low}
    return "EXPIRED",end,{"reason":"no_tp1_or_sl_hit_within_4h","horizon_seconds":HORIZON}

def evaluate_latest():
    db = sqlite3.connect(DB_PATH)
    row = db.execute(
        "SELECT event_id, signal_id, event_timestamp, data "
        "FROM signal_events "
        "WHERE event_type='NORMAL_SIGNAL_EMITTED' "
        "AND signal_id NOT IN "
        "(SELECT signal_id FROM signal_events "
        "WHERE event_type='NORMAL_SIGNAL_OUTCOME' AND state != 'PENDING') "
        "ORDER BY event_id ASC"
    ).fetchall()

    if not row:
        db.close()
        print("NO_ELIGIBLE_NORMAL_SIGNAL")
        return

    event_id, signal_id, event_timestamp, raw = row
    data = json.loads(raw)
    outcome, outcome_timestamp, evidence = evaluate_signal(
        event_timestamp, data
    )

    payload = {
        "source_event_id": event_id,
        "symbol": data["symbol"],
        "direction": data["direction"],
        "entry": data["entry"],
        "stop_loss": data["stop_loss"],
        "tp1": data["tp1"],
        "signal_timestamp": event_timestamp,
        "outcome_timestamp": outcome_timestamp,
        "horizon_seconds": HORIZON,
        "outcome": outcome,
        "evidence": evidence,
    }

    db.execute(
        "INSERT INTO signal_events "
        "(signal_id,event_type,state,event_timestamp,data) "
        "VALUES (?,?,?,?,?)",
        (
            signal_id,
            "NORMAL_SIGNAL_OUTCOME",
            outcome,
            time.time(),
            json.dumps(payload),
        ),
    )
    db.commit()
    db.close()

    print("SIGNAL_ID:", signal_id)
    print("SYMBOL:", data["symbol"])
    print("OUTCOME:", outcome)
    print("OUTCOME_TIMESTAMP:", outcome_timestamp)


if __name__ == "__main__":
    evaluate_latest()
