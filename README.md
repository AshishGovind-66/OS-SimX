# OS-SimX — Interactive Operating Systems Simulator

OS-SimX is a college-level educational web application that visualizes core Operating Systems concepts. It is a simulator, not a real kernel or a replacement for the OS scheduler.

## Features

### CPU Scheduler
- FCFS (First Come First Served)
- SJF (non-preemptive Shortest Job First)
- SRTF (preemptive Shortest Remaining Time First)
- Round Robin with configurable quantum
- Priority scheduling (non-preemptive; lower number means higher priority)
- Editable process table: PID, arrival, burst, priority
- Gantt timeline, completion/turnaround/waiting/response metrics
- Average metrics and charts

### Memory Manager
- FIFO, LRU, and Optimal page replacement
- Editable reference string and frame count
- Frame-by-frame trace, hit/fault counts, fault rate, chart

### Deadlock Lab
- Deadlock detection using allocation, request, and available matrices
- Completion sequence and blocked-process reporting
- Optional Banker's safety algorithm using a maximum-claim matrix

## Stack
- Python 3
- Flask
- HTML, CSS, JavaScript
- Chart.js for charts (loaded from a CDN when internet is available)

## Requirements
- Python 3.10+
- pip
- A browser

## Run on Ubuntu / WSL / Linux

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

If `venv` support is missing on Ubuntu:

```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

Open the URL printed in the terminal, normally `http://127.0.0.1:5000`.

Keep the terminal running while using the dashboard. Stop the server with `Ctrl+C`.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## How to use
1. Open **CPU Scheduler**.
2. Edit the process table or use the sample values.
3. Choose an algorithm and, for Round Robin, set a positive quantum.
4. Click **Run simulation** to update the Gantt chart, metrics, and charts.
5. Open **Memory Manager** to compare page replacement algorithms.
6. Open **Deadlock Lab** to enter allocation/request matrices and available resources.

## CPU metric definitions
- Completion time (CT): time when a process finishes.
- Turnaround time (TAT): `CT - Arrival Time`.
- Waiting time (WT): `TAT - Burst Time` for these single-CPU scheduling models.
- Response time (RT): first CPU start time minus arrival time.
- Average metrics are arithmetic means across the submitted processes.

## Limitations and assumptions
- Scheduling algorithms operate on a single CPU and integer time units.
- SJF and Priority are non-preemptive; SRTF is preemptive.
- Lower numeric priority is treated as higher priority.
- This is a teaching simulator, not a real-time kernel implementation.
- Deadlock detection expects current outstanding requests and an available-resource vector. Banker's algorithm uses maximum claims.
- Charts use Chart.js from a CDN; if offline, the dashboard functionality still works but charts may not load.
- This project is intended for local educational use. Flask debug mode is enabled for development; do not expose the development server to public networks.

## Project structure

```text
OS-SimX/
├── app.py
├── src/
│   ├── __init__.py
│   ├── scheduler.py
│   ├── memory.py
│   └── deadlock.py
├── templates/
│   └── index.html
├── static/
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_simulators.py
├── requirements.txt
├── run.sh
├── Makefile
├── .gitignore
└── README.md
```
