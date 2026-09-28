import json

def audit_event(event_type, data):
    return {"event_type": event_type, "data": json.loads(json.dumps(data, default=str))}
