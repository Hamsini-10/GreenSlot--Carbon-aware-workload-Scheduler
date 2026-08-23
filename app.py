import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from scheduler import recommend_schedule, check_urgent_abuse
from carbon_data import get_real_forecast, get_current_forecast_vs_actual, get_sample_price_forecast

st.set_page_config(page_title="GreenSlot", page_icon="🌱", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a1612; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f0fdf4; }
    .hero {
        background: #0f2019;
        border: 0.5px solid #1d3a2e;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .hero-top { display:flex; align-items:center; justify-content:space-between; margin-bottom: 16px; }
    .brand { font-size: 20px; font-weight: 600; color: #f0fdf4; }
    .brand-sub { font-size: 12px; color: #7a9a8b; margin-top: 2px; }
    .badge-live {
        font-size: 11px; color: #6ee7b7; background: #0f2a20;
        padding: 4px 10px; border-radius: 6px; border: 0.5px solid #1d3a2e;
    }
    .badge-sample {
        font-size: 11px; color: #fbbf24; background: #2a2410;
        padding: 4px 10px; border-radius: 6px; border: 0.5px solid #3a331d;
    }
    .stat-row { display: flex; gap: 12px; flex-wrap: wrap; }
    .stat-card {
        background: #0f2019; border: 0.5px solid #1d3a2e; border-radius: 10px;
        padding: 12px 16px; flex: 1; min-width: 140px;
    }
    .stat-label { font-size: 11px; color: #7a9a8b; }
    .stat-value { font-size: 20px; font-weight: 600; color: #f0fdf4; margin-top: 4px; }
    .stat-value.green { color: #34d399; }
    .card {
        background: #0f2019; border: 0.5px solid #1d3a2e; border-radius: 10px;
        padding: 16px; margin-bottom: 14px;
    }
    .card-title { font-size: 12px; color: #9cc4b1; margin-bottom: 10px; }
    .progress-outer { height: 6px; background: #123024; border-radius: 4px; overflow: hidden; }
    .progress-inner { height: 100%; background: #34d399; }
    .abuse-banner {
        background: #2a2410; border-left: 4px solid #f59e0b; border-radius: 8px;
        padding: 12px 16px; margin: 10px 0; color: #fde68a;
    }
    .abuse-banner strong { color: #fbbf24; }
    div.stButton > button {
        background-color: #34d399; color: #0a1612; border-radius: 10px;
        padding: 0.6em 1.6em; font-weight: 600; border: none;
    }
    div.stButton > button:hover { background-color: #6ee7b7; color: #0a1612; }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {
        background-color: #0f2019 !important; color: #f0fdf4 !important;
        border-color: #1d3a2e !important;
    }
    [data-testid="stTable"] { background: #0f2019; }
</style>
""", unsafe_allow_html=True)

if "booked_hours" not in st.session_state:
    st.session_state.booked_hours = set()
if "job_history" not in st.session_state:
    st.session_state.job_history = []
if "urgent_count" not in st.session_state:
    st.session_state.urgent_count = 0

forecast, data_source = get_real_forecast()
current = get_current_forecast_vs_actual()
current_intensity = current["actual"] if current else forecast[0]
price_forecast = get_sample_price_forecast()

total_jobs = len(st.session_state.job_history)
urgent_jobs = sum(1 for j in st.session_state.job_history if j["Urgency"] == "urgent")
flexible_jobs = total_jobs - urgent_jobs
urgent_ratio_display = f"{urgent_jobs}/{total_jobs}" if total_jobs else "0/0"
total_kg_saved = sum(j.get("kg_saved", 0) for j in st.session_state.job_history if j.get("kg_saved"))

badge_html = ('<span class="badge-live">Live · UK grid</span>' if data_source == "real"
              else '<span class="badge-sample">Sample data</span>')

st.markdown(f"""
<div class="hero">
    <div class="hero-top">
        <div>
            <div class="brand">🌱 GreenSlot</div>
            <div class="brand-sub">Carbon-aware workload scheduler</div>
        </div>
        {badge_html}
    </div>
    <div class="stat-row">
        <div class="stat-card"><div class="stat-label">Current intensity</div><div class="stat-value">{current_intensity} gCO2/kWh</div></div>
        <div class="stat-card"><div class="stat-label">Jobs scheduled</div><div class="stat-value">{total_jobs}</div></div>
        <div class="stat-card"><div class="stat-label">Urgent ratio</div><div class="stat-value">{urgent_ratio_display}</div></div>
        <div class="stat-card"><div class="stat-label">CO2 saved</div><div class="stat-value green">{total_kg_saved:.1f} kg</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

if current:
    diff = current["actual"] - current["forecast"]
    st.caption(f"Live check — forecast {current['forecast']} gCO2/kWh vs actual {current['actual']} gCO2/kWh ({diff:+.0f}).")

    if abs(diff) > 20:
        st.warning(
            f"⚠️ **Forecast anomaly detected:** actual carbon intensity differs from the forecast "
            f"by {diff:+.0f} gCO2/kWh. In production, this would trigger a reliability alert to "
            f"the scheduling team, since large forecast errors reduce confidence in recommendations."
        )

tab1, tab2, tab3 = st.tabs(["➕ Add workload", "📊 Schedule", "ℹ️ About"])

default_energy_by_type = {
    "Backup": 2.0, "Report generation": 0.5, "ML training": 15.0,
    "Batch data processing": 3.0, "Other / not sure": 1.0
}

with tab1:
    st.subheader("Add a workload")

    job_name = st.text_input("Job name", placeholder="e.g. nightly_backup")
    urgency = st.selectbox("Urgency", ["flexible", "urgent"])

    urgent_reason = ""
    if urgency == "urgent":
        urgent_reason = st.text_input("Why is this urgent? (required)")

    duration = st.number_input("Duration (hours)", min_value=1, max_value=24, value=1)

    use_deadline = st.checkbox("Set a deadline?")
    deadline = None
    if use_deadline:
        deadline = st.number_input(
            "Must finish by hour (0-23)",
            min_value=duration, max_value=23, value=max(12, duration)
        )

    job_type = st.selectbox("Job type", list(default_energy_by_type.keys()))
    energy_kwh = st.number_input(
        "Estimated energy use (kWh)",
        min_value=0.0, value=default_energy_by_type[job_type], step=0.5,
        help="Typical default — not a real measurement. Edit if known."
    )
    department = st.text_input("Department / Team (optional)", placeholder="e.g. ML Ops, Finance")

    use_combined = st.checkbox("Optimize for cost AND carbon together (simulated pricing)")
    cost_weight = 0.5
    if use_combined:
        cost_weight = st.slider("Weight: carbon vs cost", 0.0, 1.0, 0.5,
                                 help="0 = carbon only, 1 = cost only, 0.5 = balanced")

    if st.button("⚡ Get recommendation"):
        if job_name.strip() == "":
            st.warning("Please enter a job name first.")
        else:
            if urgency == "urgent":
                st.session_state.urgent_count += 1

            result = recommend_schedule(
                job_name, urgency, forecast, duration=duration,
                booked_hours=st.session_state.booked_hours,
                deadline=deadline, urgent_reason=urgent_reason,
                price_forecast=price_forecast if use_combined else None,
                cost_weight=cost_weight
            )

            if result["recommended_hour"] is None:
                st.info(f"ℹ️ {result['reason']} Try a different duration or add fewer jobs first.")
            else:
                st.success(f"Recommended hour: {result['recommended_hour']}")
                st.write(f"**Carbon intensity at that time:** {result['carbon_intensity']}")
                if result["estimated_price"] is not None:
                    st.write(f"**Simulated price at that time:** ${result['estimated_price']}/kWh")
                st.write(f"**Reason:** {result['reason']}")

            abuse_warning = check_urgent_abuse(st.session_state.urgent_count)
            if abuse_warning:
                st.markdown(f"""
                <div class="abuse-banner">
                    <strong>Possible misuse detected</strong><br>
                    <span style="font-size:13px;">{abuse_warning}</span>
                </div>
                """, unsafe_allow_html=True)

            kg_saved = 0
            if urgency == "flexible" and result["recommended_hour"] is not None:
                immediate_intensity = forecast[0]
                recommended_intensity = result["carbon_intensity"]
                if immediate_intensity > 0:
                    savings_percent = ((immediate_intensity - recommended_intensity) / immediate_intensity) * 100
                    st.info(f"**Estimated carbon reduction:** ~{savings_percent:.1f}% vs running now. *(Based on {data_source} data.)*")

                if energy_kwh and energy_kwh > 0:
                    immediate_kg = (immediate_intensity * energy_kwh) / 1000
                    recommended_kg = (recommended_intensity * energy_kwh) / 1000
                    kg_saved = immediate_kg - recommended_kg
                    st.info(f"**Estimated emissions:** now ≈ {immediate_kg:.2f} kg CO2, recommended ≈ {recommended_kg:.2f} kg CO2 "
                            f"(saving ≈ {kg_saved:.2f} kg CO2). *(Based on {energy_kwh} kWh for '{job_type}' — not measured.)*")

                if energy_kwh and energy_kwh > 0:
                    price_now = result["estimated_price"] if result["estimated_price"] is not None else price_forecast[0]
                    cost = energy_kwh * price_now
                    st.info(f"**Estimated electricity cost:** ≈ ${cost:.2f} for this job. "
                            f"*(Based on simulated hourly pricing — not real market data.)*")

            if result["recommended_hour"] is not None:
                st.session_state.job_history.append({
                    "Job": job_name, "Type": job_type, "Urgency": urgency,
                    "Department": department if department.strip() else "Unassigned",
                    "Duration (hrs)": duration, "Scheduled hour": result["recommended_hour"],
                    "Carbon intensity": result["carbon_intensity"], "kg_saved": kg_saved
                })
            st.rerun()

with tab2:
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown('<div class="card"><div class="card-title">Carbon intensity forecast</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(forecast))), y=forecast, mode="lines",
            line=dict(color="#34d399", width=2), name="Carbon intensity"
        ))
        for job in st.session_state.job_history:
            hour = job["Scheduled hour"]
            if isinstance(hour, int):
                fig.add_trace(go.Scatter(
                    x=[hour], y=[forecast[hour]],
                    mode="markers", marker=dict(size=10, color="#6ee7b7"),
                    name=job["Job"]
                ))
        fig.update_layout(
            paper_bgcolor="#0f2019", plot_bgcolor="#0f2019",
            font_color="#9cc4b1", margin=dict(l=10, r=10, t=10, b=10), height=260,
            xaxis=dict(gridcolor="#1d3a2e", title="Hour"),
            yaxis=dict(gridcolor="#1d3a2e", title="gCO2/kWh"),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card"><div class="card-title">Job urgency split</div>', unsafe_allow_html=True)
        if total_jobs > 0:
            donut = go.Figure(data=[go.Pie(
                labels=["Flexible", "Urgent"], values=[flexible_jobs, urgent_jobs],
                hole=0.6, marker=dict(colors=["#34d399", "#f59e0b"]),
                textfont=dict(color="#0a1612")
            )])
            donut.update_layout(
                paper_bgcolor="#0f2019", font_color="#9cc4b1",
                margin=dict(l=10, r=10, t=10, b=10), height=220,
                showlegend=True, legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(donut, use_container_width=True)
        else:
            st.caption("Add jobs to see the split.")
        st.markdown('</div>', unsafe_allow_html=True)

        progress_pct = min(100, int((total_kg_saved / 5) * 100)) if total_kg_saved else 0
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Scheduling mode</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:12px; color:#9cc4b1;">Optimizing for low carbon intensity</span>
                <span style="font-size:11px; color:#34d399; background:#123024; padding:2px 8px; border-radius:6px;">Active</span>
            </div>
            <div class="progress-outer"><div class="progress-inner" style="width:{progress_pct}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Jobs scheduled this session")
    if st.session_state.job_history:
        display_rows = [
            {k: v for k, v in job.items() if k != "kg_saved"}
            for job in st.session_state.job_history
        ]
        st.table(display_rows)

        df = pd.DataFrame(display_rows)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download report as CSV",
            data=csv,
            file_name="greenslot_schedule_report.csv",
            mime="text/csv"
        )

        st.subheader("Savings by department")
        dept_totals = {}
        for job in st.session_state.job_history:
            dept = job.get("Department", "Unassigned")
            dept_totals[dept] = dept_totals.get(dept, 0) + job.get("kg_saved", 0)
        for dept, kg in dept_totals.items():
            st.write(f"**{dept}**: {kg:.2f} kg CO2 saved")
    else:
        st.caption("No jobs added yet — add one in the 'Add workload' tab.")

with tab3:
    st.write("""
    **GreenSlot** schedules flexible data-center workloads during lower-carbon-intensity
    electricity periods, while urgent jobs still run immediately with no delay.

    - Real live carbon data from the UK Carbon Intensity API, with automatic fallback
    - Forecast-vs-actual anomaly detection
    - Duration- and deadline-aware scheduling
    - Conflict avoidance across multiple jobs in a session
    - Optional combined cost + carbon optimization (simulated pricing)
    - Carbon, cost, and emissions savings estimates
    - Department-level savings breakdown
    - CSV export for reporting
    - Urgent-job justification and misuse-pattern detection
    """)
    st.write("**Team:** [Team Name] | **Hackathon:** [Hackathon Name]")
    