def _validate_matrix(matrix, name):
    if not isinstance(matrix, list) or not matrix:
        raise ValueError(f"{name} must be a non-empty matrix.")
    width = len(matrix[0])
    if width == 0 or any(not isinstance(row, list) or len(row) != width for row in matrix):
        raise ValueError(f"{name} must be rectangular.")
    out = []
    for row in matrix:
        values = [int(v) for v in row]
        if any(v < 0 for v in values):
            raise ValueError(f"{name} values cannot be negative.")
        out.append(values)
    return out

def detect_deadlock(allocation, request, available):
    alloc = _validate_matrix(allocation, "Allocation")
    req = _validate_matrix(request, "Request")
    if len(alloc) != len(req) or len(alloc[0]) != len(req[0]):
        raise ValueError("Allocation and Request matrices must have the same dimensions.")
    avail = [int(x) for x in available]
    if len(avail) != len(alloc[0]) or any(x < 0 for x in avail):
        raise ValueError("Available vector must match resource count and be non-negative.")
    work = avail[:]
    finish = [all(x == 0 for x in row) for row in alloc]
    sequence = []
    changed = True
    while changed:
        changed = False
        for i in range(len(alloc)):
            if not finish[i] and all(req[i][j] <= work[j] for j in range(len(work))):
                work = [work[j] + alloc[i][j] for j in range(len(work))]
                finish[i] = True
                sequence.append(f"P{i}")
                changed = True
    deadlocked = [f"P{i}" for i, done in enumerate(finish) if not done]
    return {"deadlock": bool(deadlocked), "deadlocked_processes": deadlocked, "completion_sequence": sequence,
            "final_work": work}

def bankers_safe_sequence(allocation, max_claim, available):
    alloc = _validate_matrix(allocation, "Allocation")
    maximum = _validate_matrix(max_claim, "Max claim")
    if len(alloc) != len(maximum) or len(alloc[0]) != len(maximum[0]):
        raise ValueError("Allocation and Max claim matrices must have the same dimensions.")
    avail = [int(x) for x in available]
    if len(avail) != len(alloc[0]):
        raise ValueError("Available vector must match resource count.")
    need = [[maximum[i][j] - alloc[i][j] for j in range(len(avail))] for i in range(len(alloc))]
    if any(v < 0 for row in need for v in row):
        raise ValueError("Max claim cannot be less than current allocation.")
    work = avail[:]
    finish = [False] * len(alloc)
    seq = []
    while True:
        found = False
        for i in range(len(alloc)):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(len(work))):
                work = [work[j] + alloc[i][j] for j in range(len(work))]
                finish[i] = True
                seq.append(f"P{i}")
                found = True
        if not found:
            break
    return {"safe": all(finish), "safe_sequence": seq, "need": need,
            "unfinished_processes": [f"P{i}" for i, done in enumerate(finish) if not done]}
