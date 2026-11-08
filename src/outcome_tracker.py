import json, sqlite3, time
from src.binance_data import get_klines

DB = "a2z_scanner.db"
H = 14400
SINCE = 1794165887

def _judge(ts, d):
    lg = d["direction"] == "LONG"
    sl = float(d["stop_loss"]); tp = float(d["tp1"])
    rows = [r for r in get_klines(d["symbol"], "5m", 300) if ts * 1000 <= float(r[0]) <= (ts + H) * 1000]
    if not rows or float(rows[0][0]) > ts * 1000 + 600000:
        return "NO_DATA"
    for r in rows:
        h = float(r[2]); l = float(r[3])
        tph = h >= tp if lg else l <= tp
        slh = l <= sl if lg else h >= sl
        if tph and slh:
            return "AMBIG"
        if tph:
            return "WIN"
        if slh:
            return "LOSS"
    return "EXPIRED"

def evaluate_pending():
    db = sqlite3.connect(DB, timeout=10)
    done = {r[0] for r in db.execute("select signal_id from signal_events where event_type='NORMAL_SIGNAL_OUTCOME' and state in ('WIN','LOSS','AMBIG','EXPIRED','NO_DATA')")}
    rows = db.execute("select signal_id,event_timestamp,data from signal_events where event_type='NORMAL_SIGNAL_EMITTED' and event_timestamp>?", (SINCE,)).fetchall()
    for sid, ts, raw in rows:
        if sid in done or time.time() < ts + H:
            continue
        try:
            d = json.loads(raw)
            res = _judge(float(ts), d)
            db.execute("insert into signal_events (signal_id,event_type,state,event_timestamp,data) values (?,?,?,?,?)",
                       (sid, "NORMAL_SIGNAL_OUTCOME", res, time.time(), json.dumps({"symbol": d["symbol"], "direction": d["direction"]})))
            db.commit()
        except Exception as e:
            print("outcome error", sid, e, flush=True)
    db.close()

def report():
    db = sqlite3.connect(DB, timeout=10)
    sent = db.execute("select count(*) from signal_events where event_type='NORMAL_SIGNAL_EMITTED' and event_timestamp>?", (SINCE,)).fetchone()[0]
    print("NAYE SIGNAL BHEJE:", sent)
    for st, n in db.execute("select o.state,count(*) from signal_events o join signal_events e on e.signal_id=o.signal_id and e.event_type='NORMAL_SIGNAL_EMITTED' where o.event_type='NORMAL_SIGNAL_OUTCOME' and e.event_timestamp>? group by 1", (SINCE,)):
        print(st, n)
    db.close()

if __name__ == "__main__":
    evaluate_pending()
    report()
