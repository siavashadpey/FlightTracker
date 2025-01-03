import config
import pandas as pd
import utils
import flight_search
from flight_search import GoogleFlightScraper
import time 

def main():
    flight_data_df = utils.generate_flight_dates(config.DEPARTURE_DATE_MIN, config.DEPARTURE_DATE_MAX, config.TRIP_DURATION_MIN, config.TRIP_DURATION_MAX)

    driver = flight_search.create_driver()
    GFlights = GoogleFlightScraper(driver, config.DEPARTURE, config.ARRIVAL, config.MAX_NUMBER_OF_STOPS, config.MAX_FLIGHT_DURATION)

    flight_data_df['price'] = None
    for index, row in flight_data_df.iterrows():
    	price = GFlights.get_cheapest_flight_price(row['departure_date'], row['return_date'])

    flight_data_df = flight_data_df.sort_values(by="price", ascending=True)
    filename_prefix = f"{config.DEPARTURE}_{config.ARRIVAL}_D{config.DEPARTURE_DATE_MIN}_A{config.DEPARTURE_DATE_MAX}_TD{config.TRIP_DURATION_MIN}-{config.TRIP_DURATION_MAX}_FD{config.MAX_FLIGHT_DURATION}_S{config.MAX_NUMBER_OF_STOPS}"
    utils.save_dataframe_to_csv(flight_data_df, filename_prefix, ".")

    #time.sleep(300)


if __name__ == "__main__":
    main()