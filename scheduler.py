def recommend_schedule(job_name, urgency, forecast, duration=1, booked_hours=None, deadline=None, urgent_reason=None):
    if booked_hours is None:
        booked_hours = set()

    if urgency == "urgent":
        if not urgent_reason or not urgent_reason.strip():
            return {
                "job": job_name, "recommended_hour": None, "carbon_intensity": None,
                "reason": "Urgent jobs require a justification. Please provide a reason."
            }
        for h in range(0, duration):
            booked_hours.add(h)
        return {
            "job": job_name, "recommended_hour": 0, "carbon_intensity": forecast[0],
            "reason": f"Job is urgent ('{urgent_reason}'), so it runs immediately."
        }

    else:
        if deadline is None:
            deadline = len(forecast)
        latest_start = deadline - duration
        best_hour = None
        best_avg = None

        for start in range(0, latest_start + 1):
            if start + duration > len(forecast):
                continue
            window_hours = range(start, start + duration)
            if any(h in booked_hours for h in window_hours):
                continue
            avg = sum(forecast[start:start + duration]) / duration
            if best_avg is None or avg < best_avg:
                best_avg = avg
                best_hour = start

        if best_hour is None:
            return {
                "job": job_name, "recommended_hour": None, "carbon_intensity": None,
                "reason": f"No free slot available before deadline hour {deadline}."
            }

        for h in range(best_hour, best_hour + duration):
            booked_hours.add(h)

        return {
            "job": job_name, "recommended_hour": best_hour, "carbon_intensity": round(best_avg, 1),
            "reason": f"Hour {best_hour} is the cleanest FREE slot finishing by hour {deadline}."
        }


def check_urgent_abuse(urgent_count_this_session, threshold=3):
    if urgent_count_this_session > threshold:
        return (f"{urgent_count_this_session} jobs marked urgent this session — "
                f"this pattern would trigger a review in production.")
    return None


if __name__ == "__main__":
    sample_forecast = [180, 160, 140, 90, 60, 50, 70, 100, 150, 200,
                        220, 190, 170, 155, 130, 110, 95, 85, 100, 140,
                        175, 200, 210, 195]
    booked = set()
    print(recommend_schedule("nightly_backup", "flexible", sample_forecast, duration=1, booked_hours=booked))
    print(recommend_schedule("urgent_report", "urgent", sample_forecast, urgent_reason="Client escalation"))
    print(check_urgent_abuse(4))
    