import requests
from datetime import datetime, timezone

def get_real_forecast():
    """
    Fetches a real 24-hour carbon-intensity forecast from the UK Carbon
    Intensity API. Returns (list_of_24_values, data_source_label).
    Falls back to sample data automatically if the API fails.
    """
    sample_forecast = [180, 160, 140, 90, 60, 50, 70, 100, 150, 200,
                        220, 190, 170, 155, 130, 110, 95, 85, 100, 140,
                        175, 200, 210, 195]
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        url = f"https://api.carbonintensity.org.uk/intensity/{now}/fw24h"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()["data"]
        hourly_values = [block["intensity"]["forecast"] for block in data[::2]]

        if len(hourly_values) >= 24:
            return hourly_values[:24], "real"
        elif len(hourly_values) >= 12:
            while len(hourly_values) < 24:
                hourly_values.append(hourly_values[-1])
            return hourly_values, "real"
        else:
            return sample_forecast, "sample (API returned too little data)"
    except Exception as e:
        return sample_forecast, f"sample (API unavailable: {e})"


def get_current_forecast_vs_actual():
    """
    Demonstrates FORECAST UNCERTAINTY: fetches the CURRENT half-hour's
    predicted vs. actual carbon intensity. These can differ (e.g. sudden
    cloud cover drops solar output). Returns a dict, or None if unavailable.
    """
    try:
        response = requests.get("https://api.carbonintensity.org.uk/intensity", timeout=5)
        response.raise_for_status()
        d = response.json()["data"][0]
        return {
            "forecast": d["intensity"]["forecast"],
            "actual": d["intensity"]["actual"]
        }
    except Exception:
        return None


if __name__ == "__main__":
    forecast, source = get_real_forecast()
    print(f"Data source: {source}")
    print(f"24-hour forecast: {forecast}")

    current = get_current_forecast_vs_actual()
    if current:
        diff = current['actual'] - current['forecast']
        print(f"Forecast: {current['forecast']} | Actual: {current['actual']} | Diff: {diff:+.0f}")
