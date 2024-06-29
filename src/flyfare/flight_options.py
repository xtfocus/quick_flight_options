import argparse
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

from flyfare.models import AirportCode, CabinClass, FlightSearchOptions


def create_skyscanner_url(options: FlightSearchOptions) -> str:
    base_url = "https://www.skyscanner.com.vn/transport/flights/"
    departure_airport = options.from_airport.airport_code
    destination_airport = options.to_airport.airport_code

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
    options.add_argument("--headless")  # Doesn't show browser
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Firefox(
        options=options, service=Service(GeckoDriverManager().install())
    )

    driver.get(url)
    element = None
    source = None

    try:
        wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds
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

    if element and source:
        soup = BeautifulSoup(source, "html.parser")

        tops = soup.select_one('div[class*="TabsWithSparkle"]').select("button")
        tops_info = [top.select("div") for top in tops]
        tops_info = [[div.text for div in top] for top in tops]

        return tops_info


def main():
    parser = argparse.ArgumentParser(description="Search for flights.")

    parser.add_argument(
        "--from-airport",
        type=str,
        help="Departure airport",
        required=True,
    )

    parser.add_argument(
        "--to-airport",
        type=str,
        help="Landing airport",
        required=True,
    )

    parser.add_argument(
        "--departure-date", type=str, help="Departure date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "--return-date",
        type=str,
        nargs="?",
        default=None,
        help="Return date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "--adults", type=int, help="Number of adults", required=True, default=1
    )

    parser.add_argument(
        "--children", type=int, help="Number of children", required=False, default=0
    )

    parser.add_argument(
        "--cabin-class",
        type=str,
        help="Cabin class (economy, premiumeconomy, business, first)",
        required=True,
        default="economy",
    ),

    parser.add_argument(
        "--prefer-direct",
        type=bool,
        help="Preference for direct flights",
        required=False,
        default="false",
    )

    args = parser.parse_args()

    try:
        departure_date = datetime.strptime(args.departure_date, "%Y-%m-%d")
        return_date = (
            datetime.strptime(args.return_date, "%Y-%m-%d")
            if args.return_date
            else None
        )
        search_options = FlightSearchOptions(
            from_airport=AirportCode(airport_code=args.from_airport),
            to_airport=AirportCode(airport_code=args.to_airport),
            departure_date=departure_date,
            return_date=return_date,
            adults=args.adults,
            children=args.children,
            cabin_class=args.cabin_class,
            prefer_direct=args.prefer_direct,
        )
        url = create_skyscanner_url(search_options)
        print(search_flights(url))
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    try:
        # Set the departure date as tomorrow
        departure_date = datetime.now() + timedelta(days=1)
        # Set the return date as 2 days after the departure date
        return_date = departure_date + timedelta(days=2)

        from_airport = "han"
        to_airport = "dad"

        search_options = FlightSearchOptions(
            from_airport=AirportCode(airport_code=from_airport),
            to_airport=AirportCode(airport_code=to_airport),
            departure_date=departure_date,
            return_date=return_date,
            adults=1,
            children=0,
            cabin_class=CabinClass("economy"),
            prefer_direct=True,
        )
        print(search_options)
        print(create_skyscanner_url(search_options))
        print(search_flights(create_skyscanner_url(search_options)))
    except ValueError as e:
        print(e)
