# GreenSlot — Carbon-Aware Workload Scheduler

A hackathon prototype that schedules flexible data-center workloads during lower-carbon-intensity electricity periods, while urgent jobs run immediately.

## Problem
Data centers run many non-time-sensitive workloads immediately, regardless of grid conditions, causing avoidable emissions. This system shifts flexible jobs to greener time windows without touching business-critical work — no new hardware required.

## Features
- Urgent vs. flexible classification, with required justification for urgent jobs
- Duration- and deadline-aware scheduling
- Conflict avoidance across multiple jobs in a session
- Live UK grid carbon data, with automatic fallback and forecast-vs-actual comparison
- Carbon % and kg-CO2 emissions estimates, plus a relatable impact equivalence
- Urgent-job misuse pattern detection
- Session job list, forecast chart, and urgency split visualization

## Tech Stack
Python, Streamlit, Plotly, UK Carbon Intensity API (no key required)

## How to Run
pip install streamlit plotly requests
python -m streamlit run app.py

## Future Work
- Real infrastructure integration (Kubernetes, Airflow job queues)
- Forecast confidence modeling based on live forecast-vs-actual gaps
- Hardware-aware scheduling (GPU/resource capacity, not just time)
- Geographic load shifting across regions
- Grid-aware demand modeling to avoid new "clean hour" peaks at scale
- Live telemetry integration for precise emissions (replacing editable defaults)
- Verified urgency workflows tied to SLA metadata

## Team
Built for [Hackathon Name] by [Team Name].