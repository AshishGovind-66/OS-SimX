def simulate_page_replacement(references, frames=3, algorithm="LRU"):
    if not isinstance(references, list) or not references:
        raise ValueError("Enter a page reference string.")
    refs = [str(x).strip() for x in references]
    if any(not x for x in refs):
        raise ValueError("Page references cannot be empty.")
    frames = int(frames)
    if frames <= 0 or frames > 20:
        raise ValueError("Frame count must be between 1 and 20.")
    algorithm = str(algorithm).upper()
    if algorithm not in {"FIFO", "LRU", "OPTIMAL"}:
        raise ValueError("Algorithm must be FIFO, LRU, or OPTIMAL.")
    memory = []
    queue = []
    last_used = {}
    rows = []
    faults = 0
    for i, page in enumerate(refs):
        hit = page in memory
        replaced = None
        if not hit:
            faults += 1
            if len(memory) < frames:
                memory.append(page)
                queue.append(page)
            else:
                if algorithm == "FIFO":
                    victim = queue.pop(0)
                elif algorithm == "LRU":
                    victim = min(memory, key=lambda x: last_used.get(x, -1))
                    queue.remove(victim)
                else:
                    future = refs[i + 1:]
                    distances = {}
                    for candidate in memory:
                        distances[candidate] = future.index(candidate) if candidate in future else float("inf")
                    victim = max(memory, key=lambda x: distances[x])
                    queue.remove(victim)
                replaced = victim
                memory[memory.index(victim)] = page
                queue.append(page)
        last_used[page] = i
        rows.append({"page": page, "frames": memory.copy(), "hit": hit, "fault": not hit, "replaced": replaced})
    return {"algorithm": algorithm, "frames_count": frames, "references": refs,
            "rows": rows, "faults": faults, "hits": len(refs) - faults,
            "fault_rate": round(faults / len(refs) * 100, 2)}
