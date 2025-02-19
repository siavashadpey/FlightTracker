from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import logging
import re 
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_driver():
    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")  # Use the new headless mode
    # or chrome_options.add_argument("--headless") for older versions
    return webdriver.Chrome(options=chrome_options)

class FlightScraper(ABC):
    def __init__(self, driver):
        self.driver = driver

    @abstractmethod
    def get_cheapest_flight_price(self, dep_date, ret_date):
        pass

    def log_info(self, message):
        logging.info(f"{self.__class__.__name__}: {message}")

    def log_error(self, message):
        logging.error(f"{self.__class__.__name__}: {message}")

    def log_warning(self, message):
        logging.warning(f"{self.__class__.__name__}: {message}")

wait_time = 10
max_tries = 5
class GoogleFlightScraper(FlightScraper):
    def __init__(self, driver, departure, arrival, max_nb_stops, max_flight_duration):
        super().__init__(driver)
        self.set_initial_page_persist(departure, arrival, max_nb_stops, max_flight_duration)

    def set_initial_page_persist(self, departure, arrival, max_nb_stops, max_flight_duration):
        StatusOK = False
        counter = 0
        dep_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        ret_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        while (not StatusOK and counter < max_tries):
            StatusOK = self.set_initial_page(departure, arrival, max_nb_stops, max_flight_duration, dep_date, ret_date)
            counter += 1
                
    def set_initial_page(self, departure, arrival, max_nb_stops, max_flight_duration, dep_date, ret_date):
        """
        Sets up initial page, after which only the dates need to be changed.
        """
        try:
            self.driver.get("https://www.google.com/flights")
            WebDriverWait(self.driver, wait_time).until(EC.url_contains("flights")) #Wait for the url to contains flight
            self.log_info("Opened Google Flights.")
    
            if not self.set_airport('Where from?', departure):
                return False
    
            if not self.set_airport('Where to? ', arrival): # note extra whitespace
                return False
    
            if not self.set_travel_date('Departure', dep_date):
                return False
    
            if not self.set_travel_date('Return', ret_date):
                return False
    
            if not self.search_for_flights():
                return False
    
            #time.sleep(200)
    
            if not self.set_sort_by_price():
                return False
    
            if not self.set_stops_constraint(max_nb_stops):
                return False
    
            if not self.set_duration_constraint(max_flight_duration):
                return False
    
            #cheapest_tab = WebDriverWait(driver, wait_time).until(
            #EC.element_to_be_clickable((By.XPATH, "//div[text()='Cheapest']"))
            #)
            #cheapest_tab.click()
            #time.sleep(1)
    
            #time.sleep(20)
    
        except TimeoutException:
            self.log_error("Timeout while setting up initial page.")
            return False
        except:
            self.log_error("Error while setting up initial page.")
            return None
    
        return True
    
    def set_travel_date(self, flight_type, date):
        try:
            # Find the departure date element and click it
            date_element = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//input[@aria-label='{flight_type}']"))
            )
            date_element.send_keys({date})
            date_element.send_keys(Keys.TAB)
            date_element.send_keys(Keys.RETURN)
            time.sleep(1) 
            self.log_info(f"Selected {flight_type} date: {date}")
        except TimeoutException:
            self.log_error("Timeout while selecting {flight_type} date.")
            return False
    
        return True

    def set_airport(self, flight_type_keyword, airport):
        try:
            flight_type = 'Where from?'
            ele_input = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//input[@aria-label='{flight_type_keyword}']"))
            )
            ele_input.clear()
            ele_input.send_keys(airport)
            #time.sleep(1) # TODOO change this with an explicit wait which makes sure {flight_type_keyword} has been written to ele_input
            ele_element = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[@role='option' and @data-code='{airport}']"))
            )
            ele_element.click()
            #time.sleep(1)
            self.log_info(f"Entered airport: {airport}")
        except TimeoutException:
            self.log_error("Timeout while setting airport.")
            return False
        
        return True

    def search_for_flights(self):
        try:
            search_button_locator = (By.XPATH, "//button[@aria-label='Search for flights']")
    
            # Wait for the button to be clickable
            search_button = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Search']"))
            )
            search_button.click()
            time.sleep(1) #TODO change to explicit wait to ensure search has taken effect
            self.log_info(f"Clicked search for flights.")
        except TimeoutException:
            self.log_error("Timeout while clicking search.")
            return False
    
        return True

    def set_stops_constraint(self, nb_max_stops):
        try:
            stops_button = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Stops, Not selected']"))
            )
            stops_button.click()
            time.sleep(1)
            self.log_info(f"Stops button clicked")
            time.sleep(1)
            val = nb_max_stops + 1
            one_stop_option = self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{val}']") # nb of stops + 1, capped at 2 stops, -1 nb of stops means infinte
            one_stop_option.click()
            time.sleep(1)
            self.log_info(f"Stops constraint set")
        except TimeoutException:
            self.log_error("Timeout while setting stops constraint.")
            return False
    
        return True
    
    def set_duration_constraint(self, max_duration):
        try:
            duration_button = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Duration, Not selected']"))
            )
            duration_button.click()
            self.log_info(f"Duration button clicked")
            time.sleep(1)
    
            # Wait for the slider to be present. Use a more robust locator.
            slider = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='range' and @aria-label='Duration']"))
            )
            # Set the slider value using JavaScript for reliability
            self.driver.execute_script(f"arguments[0].value = {max_duration}; arguments[0].dispatchEvent(new Event('change'));", slider)
            time.sleep(1) #Important to give google time to update the interface
            self.log_info(f"Duration constraint set")
        except TimeoutException:
            self.log_error("Timeout while setting duration constraint.")
            return False
    
        return True
    
    def set_sort_by_price(self):
        try:
            sort_dropdown = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'Sorted by')]"))
            )
            # 2. Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sort_dropdown)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", sort_dropdown)
            time.sleep(1)
            self.log_info("Clicked the sort dropdown (JavaScript).")
    
            WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='menu']"))
            )
            price_option = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//li[.//span[text()='Price']]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", price_option)
            time.sleep(1)
            price_option.click()
            time.sleep(1)
            self.log_info("Clicked sort by price.")
        except TimeoutException:
            self.log_error("Timeout while setting up sort by price.")
            return False
    
        return True
    
    def get_flight_price(self):
        try:
            departing_flights_heading = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='tabpanel'][.//h3[text()='Departing flights']]"))
            )
            self.log_info("Found flights list")
    
            price_element = WebDriverWait(departing_flights_heading, wait_time).until(  # Wait relative to tab_panel
            EC.presence_of_element_located((By.XPATH, ".//span[contains(text(),'CA$')][1]"))
            )
            self.log_info("Found cheapest flight")
    
            price_match = re.search(r"[A-Z]{2}\$([\d,]+)", price_element.text)  # Matches "CA$", "US$", etc.
            if price_match:
                price_str = price_match.group(1).replace(",", "")  # Remove commas
                flight_price = int(price_str)
                self.log_info(f"Price: {flight_price}")
                return flight_price
        except TimeoutException:
            self.log_error("Timeout while getting flight price.")
            return None
        except:
            self.log_error("Error while getting flight price.")
            return None
    
    def wait_for_specific_progress_bar(self, wait_time=20, progress_bar_xpath=None):
        """Waits for a *specific* progress bar to become invisible."""
    
        if progress_bar_xpath is None:
            self.log_error("Progress_bar_xpath must be provided.")
            return False
    
        try:
            progress_bar_locator = (By.XPATH, progress_bar_xpath)
    
            # Wait for the progress bar to be visible
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(progress_bar_locator)
            )
            self.log_info("Specific progress bar is visible. Waiting for it to become invisible...")
    
            # Wait for the progress bar to become invisible
            WebDriverWait(self.driver, wait_time).until(
                EC.invisibility_of_element_located(progress_bar_locator)
            )
            self.log_info("Specific progress bar finished!")
            return True
    
        except TimeoutException:
            self.log_error("Specific progress bar did not finish within the specified time.")
            return False
        except Exception as e:
            self.log_error(f"An unexpected error occurred: {e}")
            return False
    
    def wait_for_all_progress_bars(self, wait_time=20, progress_bar_xpath="//div[@role='progressbar']"):
        """Waits for *all* progress bars to become invisible."""
        try:
            progress_bar_locator = (By.XPATH, progress_bar_xpath)
    
            # Wait for at least one progress bar to be present
            WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(progress_bar_locator))
    
            # Wait for *all* progress bars to become invisible
            WebDriverWait(self.driver, wait_time).until(
                EC.invisibility_of_element_located(progress_bar_locator)
            )
            self.log_info("All progress bars finished!")
            return True
    
        except TimeoutException:
            self.log_error("Progress bars did not finish within the specified time.")
            return False
        except Exception as e:
            self.log_error(f"An unexpected error occurred: {e}")
            return False
    
    def get_cheapest_flight_price(self, dep_date, ret_date):
        counter = 0
        while (counter < max_tries):
            price = self.get_cheapest_flight_price_not_persist(dep_date, ret_date)
            if price is not None:
                return price
            counter += 1
        return None

    def get_cheapest_flight_price_not_persist(self, dep_date, ret_date):
        try:
            if not self.set_travel_date('Departure', dep_date):
                return None
    
            if not self.set_travel_date('Return', ret_date):
                return None
    
            self.driver.refresh()
            time.sleep(1)
            self.log_info("refreshed")
    
            self.wait_for_all_progress_bars()
            #time.sleep(20)
            time.sleep(1)
            #no_results_message = WebDriverWait(driver, 30).until(
            #EC.presence_of_element_located((By.XPATH, "//div[text()='No results returned.']"))
            #)
            #time.sleep(1)
            self.log_info("Finished searching for cheapest flight.")
            return self.get_flight_price()
        except TimeoutException:
            self.log_error("Timeout while setting dates or getting price.")
            return None

class KayakScraper(FlightScraper):
    def __init__(self, driver, departure, arrival, max_nb_stops, max_flight_duration):
        super().__init__(driver)
        self.url_template = self.set_initial_page(departure, arrival, max_nb_stops, max_flight_duration)

    def set_initial_page(self, departure, arrival, max_nb_stops, max_flight_duration):
        max_flight_duration_str = self.get_max_flight_duration_str(max_flight_duration)
        nb_stops_str = self.get_nb_stops_str(max_nb_stops)
        dep_date_ph = "{departure_date}"
        ret_date_ph = "{return_date}"
        url_template = f"https://www.ca.kayak.com/flights/{departure}-{arrival}/{dep_date_ph}/{ret_date_ph}?sort=price_a&fs={max_flight_duration_str}{nb_stops_str}"
        return url_template

    def get_cheapest_flight_price(self, dep_date, ret_date):
        counter = 0
        while (counter < max_tries):
            price = self.get_cheapest_flight_price_not_persist(dep_date, ret_date)
            if price is not None:
                return price
            counter += 1
        return None

    def get_cheapest_flight_price_not_persist(self, dep_date, ret_date):
        try:
            url = self.url_template.format(departure_date = dep_date, return_date = ret_date)
            self.driver.get(url)
            self.log_info("Opened Kayak.")
        
            # XPath using role and class
            progress_bar_locator = (By.XPATH, "//div[contains(@class,'progress')]//div[@role='progressbar']")
            
            # Wait for the element to be present
            WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(progress_bar_locator))
            self.log_info("Found progress bar.")
        
            #Wait for the attribute to change
            WebDriverWait(self.driver, 90).until(EC.invisibility_of_element_located(progress_bar_locator))#, "aria-hidden", "true"))
            self.log_info("Progress completed.")
            time.sleep(1)
        
            cheapest_option = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Cheapest']"))
            )
        
            # Extract the price text. The structure is now more flexible
            price_element = cheapest_option.find_element(By.XPATH, ".//span[contains(text(),'$')]") #Finds the first span containing a dollar sign
            self.log_info("Found cheapest price.")
            #time.sleep(20)
            price_text = price_element.text
            # Extract the numerical price using regex
            price_match = re.search(r"\bC\$ ([\d,]+)", price_text) 
            if price_match:
                price_str = price_match.group(1).replace(",", "")
                price = int(price_str)
                self.log_info(f"Cheapest price found: {price}")
                #time.sleep(10)
                return price
            else:
                self.log_warning(f"Price format not found in 'Cheapest' option: {price_text}")
                return None
        except TimeoutException:
            self.log_error("Timeout while setting dates or getting price.")
            return None
        #time.sleep(200)

    def get_max_flight_duration_str(self, fd_hrs):
        fd_mins = fd_hrs * 60
        return f"legdur=-{fd_mins}"

    def get_nb_stops_str(self, max_nb_stops):
        match max_nb_stops:
            case -1 | 2:
                return f";"
            case 0:
                return f";stops=~0"
            case 1:
                return f";stops=-2"
