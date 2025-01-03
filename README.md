# Flight Search Script

**This Python script automates finding the cheapest flights for your next trip!** ✈️

Is your departure date and your trip duration flexible? Well this repo will find the best priced flights between 2 cities for a range of departure dates and a range of trip duration. It currently supports constraints on the number of stops and flight duration.

**How to Use:**

1.  **Prerequisites:**
    *   Python 3.x
    *   **Install required Python libraries:**
        ```bash
        pip install -r requirements.txt
        ```
    *   A WebDriver for your browser (download from [https://sites.google.com/a/chromium.org/chromedriver/](https://www.google.com/url?sa=E&source=gmail&q=https://sites.google.com/a/chromium.org/chromedriver/))
    *   Place the WebDriver in your project directory or configure its path.
2.  **Configuration:**
    *   Edit `config.py` to set your desired search parameters:
        *   `DEPARTURE`: Your departure airport code (e.g., "YYZ")
        *   `ARRIVAL`: Your arrival airport code (e.g., "LAX")
        *   `MAX_NUMBER_OF_STOPS`: Maximum number of allowed stops (0 for direct flights)
        *   `MAX_FLIGHT_DURATION`: Maximum flight duration (in hours)
        *   `DEPARTURE_DATE_MIN`: Minimum departure date (YYYY-MM-DD format)
        *   `DEPARTURE_DATE_MAX`: Maximum departure date (YYYY-MM-DD format)
        *   `TRIP_DURATION_MIN`: Minimum trip duration (in days)
        *   `TRIP_DURATION_MAX`: Maximum trip duration (in days)
3.  **Run the Script:**
    *   Open a terminal in your project directory and run `python main.py`.
    *   
```bash
pip install -r requirements.txt
