import config
import pandas as pd
import utils
import flight_search
from flight_search import GoogleFlightScraper, KayakScraper
import time 
import concurrent.futures

def google_flights_data_df(flight_data_df):
    driver = flight_search.create_driver()
    FlightScraper = GoogleFlightScraper(driver, config.DEPARTURE, config.ARRIVAL, config.MAX_NUMBER_OF_STOPS, config.MAX_FLIGHT_DURATION)
    flight_data_df['price'] = None
    for index, row in flight_data_df.iterrows():
    	flight_data_df.at[index, 'price'] = FlightScraper.get_cheapest_flight_price(row['departure_date'], row['return_date'])

    flight_data_df = flight_data_df.sort_values(by="price", ascending=True)
    filename_prefix = f"{config.DEPARTURE}_{config.ARRIVAL}_D{config.DEPARTURE_DATE_MIN}_A{config.DEPARTURE_DATE_MAX}_TD{config.TRIP_DURATION_MIN}-{config.TRIP_DURATION_MAX}_FD{config.MAX_FLIGHT_DURATION}_S{config.MAX_NUMBER_OF_STOPS}_Google"
    utils.save_dataframe_to_csv(flight_data_df, filename_prefix, "./data/")

    flight_data_df['site'] = "google"
    driver.quit()
    print(flight_data_df)
    return flight_data_df

def kayak_data_df(flight_data_df):
    driver = flight_search.create_driver()
    FlightScraper = KayakScraper(driver, config.DEPARTURE, config.ARRIVAL, config.MAX_NUMBER_OF_STOPS, config.MAX_FLIGHT_DURATION)

    flight_data_df['price'] = None
    for index, row in flight_data_df.iterrows():
    	flight_data_df.at[index, 'price'] = FlightScraper.get_cheapest_flight_price(row['departure_date'], row['return_date'])

    flight_data_df = flight_data_df.sort_values(by="price", ascending=True)
    filename_prefix = f"{config.DEPARTURE}_{config.ARRIVAL}_D{config.DEPARTURE_DATE_MIN}_A{config.DEPARTURE_DATE_MAX}_TD{config.TRIP_DURATION_MIN}-{config.TRIP_DURATION_MAX}_FD{config.MAX_FLIGHT_DURATION}_S{config.MAX_NUMBER_OF_STOPS}_Kayak"
    utils.save_dataframe_to_csv(flight_data_df, filename_prefix, "./data/")

    flight_data_df['site'] = "kayak"
    driver.quit()
    print(flight_data_df)
    return flight_data_df

def main():
    flight_data_df = utils.generate_flight_dates(config.DEPARTURE_DATE_MIN, config.DEPARTURE_DATE_MAX, config.TRIP_DURATION_MIN, config.TRIP_DURATION_MAX)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # Limit to 2 workers
        google_future = executor.submit(google_flights_data_df, flight_data_df.copy())
        kayak_future = executor.submit(kayak_data_df, flight_data_df.copy())

        google_df = google_future.result()
        kayak_df = kayak_future.result()

    '''
    # serilized version
    google_df = google_flights_data_df(flight_data_df.copy())  # Call functions directly
    kayak_df = kayak_data_df(flight_data_df.copy())
    '''
    if google_df is not None and kayak_df is not None:
        combined_df = pd.concat([google_df, kayak_df], ignore_index=True)
        combined_df = combined_df.sort_values(by="price", ascending=True)
        filename_prefix = f"{config.DEPARTURE}_{config.ARRIVAL}_Combined_D{config.DEPARTURE_DATE_MIN}_A{config.DEPARTURE_DATE_MAX}_TD{config.TRIP_DURATION_MIN}-{config.TRIP_DURATION_MAX}_FD{config.MAX_FLIGHT_DURATION}_S{config.MAX_NUMBER_OF_STOPS}"
        utils.save_dataframe_to_csv(combined_df, filename_prefix, "./data")



if __name__ == "__main__":
    main()