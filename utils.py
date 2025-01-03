from datetime import datetime, timedelta
import pandas as pd

def generate_flight_dates(dep_date_min_str, dep_date_max_str, duration_min, duration_max):
    departure_date_min = datetime.strptime(dep_date_min_str, "%Y-%m-%d")
    departure_date_max = datetime.strptime(dep_date_max_str, "%Y-%m-%d")

    flight_dates = []

    # Iterate through possible departure dates and trip durations
    for duration in range(duration_min - 1, duration_max):
        current_departure_date = departure_date_min
        while current_departure_date <= departure_date_max:
            return_date = current_departure_date + timedelta(days=duration)
            flight_dates.append({
                "departure_date": current_departure_date.strftime("%Y-%m-%d"),
                "return_date": return_date.strftime("%Y-%m-%d")
            })

            current_departure_date += timedelta(days=1)  # Move to the next day

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(flight_dates)
    return df