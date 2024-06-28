from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from models import FlightSearchOptions


def create_skyscanner_url(options: FlightSearchOptions) -> str:
    base_url = "https://www.skyscanner.com.vn/transport/flights/"
    departure_airport = "han"
    destination_airport = "dad"

    # Format the dates to match the expected format (yymmdd)
    formatted_departure_date = options.departure_date.strftime("%y%m%d")
    formatted_return_date = (
        options.return_date.strftime("%y%m%d") if options.return_date else ""
    )

    # Build the URL path
    if formatted_return_date:
        path = f"{departure_airport}/{destination_airport}/{formatted_departure_date}/{formatted_return_date}/"
    else:
        path = f"{departure_airport}/{destination_airport}/{formatted_departure_date}/"

    # Build the query parameters
    query_parameters = {
        "adults": options.adults,
        "cabinclass": options.cabin_class,
        "children": options.children,
        "ref": "home",
        "rtn": 1 if options.return_date else 0,
        "preferdirects": str(options.prefer_direct).lower(),
    }

    # Format query parameters
    query_string = "&".join(
        [f"{key}={value}" for key, value in query_parameters.items()]
    )

    # Construct the full URL
    full_url = f"{base_url}{path}?{query_string}"

    return full_url


def search_flights(url):
    options = Options()
    ua = UserAgent()
    user_agent = ua.random

    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--headless")

    driver = webdriver.Firefox(
        options=options, service=Service(GeckoDriverManager().install())
    )

    driver.get(url)
    element = None

    try:
        wait = WebDriverWait(driver, 30)  # Wait for up to 10 seconds
        element = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[class*="TicketStub"]')
            )
        )

        source = driver.page_source

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the WebDriver
        driver.quit()

    if element:
        soup = BeautifulSoup(source)

        tops = soup.select_one('div[class*="TabsWithSparkle"]').select("button")
        tops_info = [top.select("div") for top in tops]
        tops_info = [[div.text for div in top] for top in tops]

        return tops_info


if __name__ == "__main__":
    try:
        # Set the departure date as tomorrow
        departure_date = datetime.now() + timedelta(days=1)
        # Set the return date as 2 days after the departure date
        return_date = departure_date + timedelta(days=2)

        search_options = FlightSearchOptions(
            departure_date=departure_date,
            return_date=return_date,
            adults=1,
            children=0,
            cabin_class="economy",
            prefer_direct=True,
        )
        print(search_options)
        print(create_skyscanner_url(search_options))
        print(search_flights(create_skyscanner_url(search_options)))
    except ValueError as e:
        print(e)
