# GreenSlot — Carbon-Aware Workload Scheduler

A hackathon prototype that schedules flexible data-center workloads during lower-carbon-intensity electricity periods, while urgent jobs run immediately.

## Problem
Data centers run many non-time-sensitive workloads immediately, regardless of grid conditions, causing avoidable emissions. This system shifts flexible jobs to greener time windows without touching business-critical work — no new hardware required.

## Features
- Urgent vs. flexible classification, with required justification for urgent jobs
- Duration- and deadline-aware scheduling
- Conflict avoidance across multiple jobs in a session
- Live UK grid carbon data, with automatic fallback and forecast-vs-actual anomaly detection
- Optional combined cost + carbon optimization (simulated pricing)
- Carbon % and kg-CO2 emissions estimates
- Department-level savings breakdown
- CSV export for reporting
- Urgent-job misuse pattern detection

## Tech Stack
Python, Streamlit, Plotly, Pandas, UK Carbon Intensity API (no key required)

## How to Run
pip install streamlit plotly requests pandas
python -m streamlit run app.py

## Future Work (Roadmap to Enterprise SaaS)
- Multi-region orchestration (route jobs to the cleanest region, not just time)
- Native connectors for Kubernetes, Airflow, Slurm
- ESG compliance reporting dashboard
- Real-time electricity pricing integration (replacing simulated pricing)
- SLA-aware prioritization with adaptive learning
- API-first architecture for customer-built integrations
- Verified urgency workflows tied to SLA metadata

## Team
Built for [HakITxMRDU] by [Hamsini and team].