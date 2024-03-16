import os
import requests
from dotenv import load_dotenv

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

    response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        return None  # error
    else:
        # error, any other status codes
        return None







def kiwi_flight_search(origin, destination, date_from, date_to, return_from, return_to, partner_market):
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
        "partner_market": partner_market
    }

    headers = {
        "apikey": KIWI_KEY
    }

    response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        return None #error
    else:
        return None #error, any other status codes