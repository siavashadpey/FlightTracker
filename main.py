import config
import pandas as pd
import utils
import flight_search
import time 
max_tries = 5
def main():
    flight_data_df = utils.generate_flight_dates(config.DEPARTURE_DATE_MIN, config.DEPARTURE_DATE_MAX, config.TRIP_DURATION_MIN, config.TRIP_DURATION_MAX)
    first_flight = flight_data_df.iloc[-1]
    
    driver = flight_search.get_driver()

    StatusOK = False
    counter = 0
    while (not StatusOK and counter < max_tries):
        StatusOK = flight_search.set_initial_page(driver, config.DEPARTURE, config.ARRIVAL, config.MAX_NUMBER_OF_STOPS, config.MAX_FLIGHT_DURATION, first_flight['departure_date'], first_flight['return_date'])
        counter += 1

    flight_data_df['price'] = None
    for index, row in flight_data_df.iterrows():
        StatusOK = False
        counter = 0
        while (not StatusOK and counter < max_tries):
            price = flight_search.get_cheapest_flight_price(driver, row['departure_date'], row['return_date'])
            counter += 1
            StatusOK = price != None
            if StatusOK:
            	flight_data_df.at[index, 'price'] = price

    flight_data_df = flight_data_df.sort_values(by="price", ascending=True)
    filename_prefix = f"{config.DEPARTURE}_{config.ARRIVAL}_D{config.DEPARTURE_DATE_MIN}_A{config.DEPARTURE_DATE_MAX}_TD{config.TRIP_DURATION_MIN}-{config.TRIP_DURATION_MAX}_FD{config.MAX_FLIGHT_DURATION}_S{config.MAX_NUMBER_OF_STOPS}"
    utils.save_dataframe_to_csv(flight_data_df, filename_prefix, ".")

    #time.sleep(300)


if __name__ == "__main__":
    main()