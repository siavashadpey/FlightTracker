from datetime import datetime, timedelta
import pandas as pd
import os 

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

def save_dataframe_to_csv(df, filename_prefix, output_dir):
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    filename = f"{filename_prefix}_{timestamp}.csv"

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True) #exist_ok avoids raising an exception if the folder already exists

    filepath = os.path.join(output_dir, filename)

    # Save DataFrame to CSV
    df.to_csv(filepath, index=False, encoding='utf-8')  # index=False prevents writing row indices

    print(f"DataFrame saved to: {filepath}")
