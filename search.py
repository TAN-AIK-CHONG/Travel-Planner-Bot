import os
import requests
from dotenv import load_dotenv
import urllib.parse

## Returns list of possible IATA based on city name inputted
def kiwi_location_search(term, locale, location_types, limit, active_only):
    load_dotenv('.env')
    KIWI_KEY = os.getenv('KIWI_KEY')
    endpoint = "https://tequila-api.kiwi.com/locations/query"

    params = {
        "term": term,
        "locale": locale,
        "location_types": location_types,
        "limit": limit,
        "active_only": active_only
    }

    headers = {
        "apikey": KIWI_KEY
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None  # Return None if there's an error







def kiwi_flight_search(origin, destination, date_from, date_to, return_from, return_to, partner_market, currency):
    load_dotenv('.env')
    KIWI_KEY = os.getenv('KIWI_KEY') 
    endpoint = "https://tequila-api.kiwi.com/v2/search"

    params = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": date_from,
        "date_to": date_to,
        "return_from": return_from,
        "return_to": return_to,
        "partner_market": partner_market,
        "curr": currency
    }

    headers = {
        "apikey": KIWI_KEY
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX and 5XX status codes

        data = response.json()
        return data  # This will contain flight search results
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None