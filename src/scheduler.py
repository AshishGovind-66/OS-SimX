from collections import deque

ALGORITHMS = {"FCFS", "SJF", "SRTF", "RR", "PRIORITY"}

def _normalize(processes):
    if not isinstance(processes, list) or not processes:
        raise ValueError("Add at least one process.")
    out = []
    seen = set()
    for i, p in enumerate(processes):
        pid = str(p.get("pid", f"P{i+1}")).strip()
        if not pid:
            raise ValueError("Process IDs cannot be empty.")
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        seen.add(pid)
        arrival = int(p.get("arrival", 0))
        burst = int(p.get("burst", 1))
        priority = int(p.get("priority", 1))
        if arrival < 0:
            raise ValueError(f"{pid}: arrival time must be >= 0.")
        if burst <= 0:
            raise ValueError(f"{pid}: burst time must be > 0.")
        out.append({"pid": pid, "arrival": arrival, "burst": burst, "priority": priority})
    return out

def simulate_cpu(processes, algorithm="RR", quantum=2):
    procs = _normalize(processes)
    algorithm = str(algorithm).upper()
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Algorithm must be one of: {', '.join(sorted(ALGORITHMS))}.")
    if algorithm == "RR" and int(quantum) <= 0:
        raise ValueError("Round Robin quantum must be greater than zero.")

    remaining = {p["pid"]: p["burst"] for p in procs}
    by_pid = {p["pid"]: p for p in procs}
    first_start = {}
    completion = {}
    segments = []
    time = 0
    ready = deque()
    pending = sorted(procs, key=lambda p: (p["arrival"], p["pid"]))
    idx = 0

    def add_segment(pid, start, end):
        if end <= start:
            return
        if segments and segments[-1]["pid"] == pid and segments[-1]["end"] == start:
            segments[-1]["end"] = end
        else:
            segments.append({"pid": pid, "start": start, "end": end})

    if algorithm == "FCFS":
        for p in pending:
            start = max(time, p["arrival"])
            add_segment(p["pid"] if start == time else "IDLE", time, start)
            first_start.setdefault(p["pid"], start)
            end = start + p["burst"]
            add_segment(p["pid"], start, end)
            time = end
            completion[p["pid"]] = end
    elif algorithm in ("SJF", "PRIORITY"):
        unfinished = {p["pid"] for p in procs}
        while unfinished:
            available = [by_pid[pid] for pid in unfinished if by_pid[pid]["arrival"] <= time]
            if not available:
                next_time = min(by_pid[pid]["arrival"] for pid in unfinished)
                add_segment("IDLE", time, next_time)
                time = next_time
                continue
            if algorithm == "SJF":
                chosen = min(available, key=lambda p: (p["burst"], p["arrival"], p["pid"]))
            else:
                chosen = min(available, key=lambda p: (p["priority"], p["arrival"], p["pid"]))
            start = time
            first_start[chosen["pid"]] = start
            end = time + remaining[chosen["pid"]]
            add_segment(chosen["pid"], start, end)
            time = end
            completion[chosen["pid"]] = time
            unfinished.remove(chosen["pid"])
    elif algorithm == "SRTF":
        unfinished = {p["pid"] for p in procs}
        while unfinished:
            available = [by_pid[pid] for pid in unfinished if by_pid[pid]["arrival"] <= time]
            if not available:
                next_time = min(by_pid[pid]["arrival"] for pid in unfinished)
                add_segment("IDLE", time, next_time)
                time = next_time
                continue
            chosen = min(available, key=lambda p: (remaining[p["pid"]], p["arrival"], p["pid"]))
            first_start.setdefault(chosen["pid"], time)
            end = time + 1
            add_segment(chosen["pid"], time, end)
            remaining[chosen["pid"]] -= 1
            time = end
            if remaining[chosen["pid"]] == 0:
                completion[chosen["pid"]] = time
                unfinished.remove(chosen["pid"])
    else:  # Round Robin
        time = min(p["arrival"] for p in pending)
        while idx < len(pending) or ready:
            while idx < len(pending) and pending[idx]["arrival"] <= time:
                ready.append(pending[idx]["pid"])
                idx += 1
            if not ready:
                next_time = pending[idx]["arrival"]
                add_segment("IDLE", time, next_time)
                time = next_time
                continue
            pid = ready.popleft()
            first_start.setdefault(pid, time)
            run_for = min(int(quantum), remaining[pid])
            start, end = time, time + run_for
            add_segment(pid, start, end)
            time = end
            remaining[pid] -= run_for
            while idx < len(pending) and pending[idx]["arrival"] <= time:
                ready.append(pending[idx]["pid"])
                idx += 1
            if remaining[pid] > 0:
                ready.append(pid)
            else:
                completion[pid] = time

    metrics = []
    for p in procs:
        pid = p["pid"]
        turnaround = completion[pid] - p["arrival"]
        waiting = turnaround - p["burst"]
        response = first_start[pid] - p["arrival"]
        metrics.append({
            "pid": pid, "arrival": p["arrival"], "burst": p["burst"],
            "priority": p["priority"], "completion": completion[pid],
            "turnaround": turnaround, "waiting": waiting, "response": response
        })
    count = len(metrics)
    return {
        "algorithm": algorithm,
        "quantum": int(quantum) if algorithm == "RR" else None,
        "segments": segments,
        "metrics": metrics,
        "averages": {
            "waiting": round(sum(m["waiting"] for m in metrics) / count, 2),
            "turnaround": round(sum(m["turnaround"] for m in metrics) / count, 2),
            "response": round(sum(m["response"] for m in metrics) / count, 2),
        },
        "total_time": max(s["end"] for s in segments) if segments else 0,
        "process_count": count
    }
