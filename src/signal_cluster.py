def build_signal_cluster(signals):
    groups = {}
    for signal in signals:
        key = signal.get("direction")
        groups.setdefault(key, []).append(signal)
    return {
        "clusters": groups,
        "cluster_count": len(groups),
        "signal_count": len(signals),
    }
