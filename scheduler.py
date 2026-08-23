def recommend_schedule(job_name, urgency, forecast, duration=1, booked_hours=None, deadline=None,
                        urgent_reason=None, price_forecast=None, cost_weight=0.5):
    """
    job_name: label for the job
    urgency: "urgent" or "flexible"
    forecast: list of hourly carbon-intensity numbers
    duration: hours the job needs to run
    booked_hours: a set tracking hours already claimed by earlier jobs
    deadline: latest hour (0-23) the job must FINISH by (flexible only)
    urgent_reason: required justification text if urgency == "urgent"
    price_forecast: OPTIONAL list of hourly electricity price numbers, same length as forecast.
                     If provided, scheduling considers BOTH carbon and cost together.
                     If not provided, behaves exactly as before (carbon only).
    cost_weight: how much to weigh cost vs carbon (0 = carbon only, 1 = cost only, 0.5 = equal)
    """
    if booked_hours is None:
        booked_hours = set()

    if urgency == "urgent":
        if not urgent_reason or not urgent_reason.strip():
            return {
                "job": job_name, "recommended_hour": None, "carbon_intensity": None,
                "estimated_price": None,
                "reason": "Urgent jobs require a justification. Please provide a reason."
            }
        for h in range(0, duration):
            booked_hours.add(h)
        return {
            "job": job_name, "recommended_hour": 0, "carbon_intensity": forecast[0],
            "estimated_price": price_forecast[0] if price_forecast else None,
            "reason": f"Job is urgent ('{urgent_reason}'), so it runs immediately."
        }

    else:
        if deadline is None:
            deadline = len(forecast)
        latest_start = deadline - duration

        candidates = []
        for start in range(0, latest_start + 1):
            if start < 0 or start + duration > len(forecast):
                continue
            window_hours = range(start, start + duration)
            if any(h in booked_hours for h in window_hours):
                continue
            avg_carbon = sum(forecast[start:start + duration]) / duration
            avg_price = None
            if price_forecast:
                avg_price = sum(price_forecast[start:start + duration]) / duration
            candidates.append((start, avg_carbon, avg_price))

        if not candidates:
            return {
                "job": job_name, "recommended_hour": None, "carbon_intensity": None,
                "estimated_price": None,
                "reason": f"No free slot available before deadline hour {deadline}."
            }

        best_hour = None
        best_avg_carbon = None
        best_avg_price = None

        if price_forecast:
            carbon_values = [c[1] for c in candidates]
            price_values = [c[2] for c in candidates]
            c_min, c_max = min(carbon_values), max(carbon_values)
            p_min, p_max = min(price_values), max(price_values)

            best_score = None
            for start, avg_carbon, avg_price in candidates:
                norm_carbon = 0 if c_max == c_min else (avg_carbon - c_min) / (c_max - c_min)
                norm_price = 0 if p_max == p_min else (avg_price - p_min) / (p_max - p_min)
                combined_score = (1 - cost_weight) * norm_carbon + cost_weight * norm_price

                if best_score is None or combined_score < best_score:
                    best_score = combined_score
                    best_hour = start
                    best_avg_carbon = avg_carbon
                    best_avg_price = avg_price
        else:
            for start, avg_carbon, _ in candidates:
                if best_avg_carbon is None or avg_carbon < best_avg_carbon:
                    best_avg_carbon = avg_carbon
                    best_hour = start

        for h in range(best_hour, best_hour + duration):
            booked_hours.add(h)

        reason = f"Hour {best_hour} is the cleanest FREE slot finishing by hour {deadline}."
        if price_forecast:
            reason = (f"Hour {best_hour} best balances carbon intensity and electricity cost "
                      f"(weighted {int((1-cost_weight)*100)}% carbon / {int(cost_weight*100)}% cost), "
                      f"finishing by hour {deadline}.")

        return {
            "job": job_name, "recommended_hour": best_hour,
            "carbon_intensity": round(best_avg_carbon, 1),
            "estimated_price": round(best_avg_price, 3) if best_avg_price is not None else None,
            "reason": reason
        }


def check_urgent_abuse(urgent_count_this_session, threshold=3):
    """Flags a suspicious PATTERN (not truth) — many jobs marked urgent in one session."""
    if urgent_count_this_session > threshold:
        return (f"{urgent_count_this_session} jobs marked urgent this session — "
                f"this pattern would trigger a review in production.")
    return None


if __name__ == "__main__":
    sample_forecast = [180, 160, 140, 90, 60, 50, 70, 100, 150, 200,
                        220, 190, 170, 155, 130, 110, 95, 85, 100, 140,
                        175, 200, 210, 195]
    sample_price = [0.10, 0.10, 0.09, 0.09, 0.08, 0.08, 0.09, 0.11, 0.14, 0.18,
                     0.22, 0.20, 0.18, 0.17, 0.15, 0.13, 0.12, 0.12, 0.14, 0.17,
                     0.20, 0.19, 0.16, 0.12]
    booked = set()
    print(recommend_schedule("nightly_backup", "flexible", sample_forecast, duration=1, booked_hours=booked))
    print(recommend_schedule("ml_training", "flexible", sample_forecast, duration=3,
                              booked_hours=set(), price_forecast=sample_price, cost_weight=0.5))
    print(recommend_schedule("urgent_report", "urgent", sample_forecast, urgent_reason="Client escalation"))
    print(check_urgent_abuse(4))
    