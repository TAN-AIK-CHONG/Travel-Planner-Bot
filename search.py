import os
import requests
from dotenv import load_dotenv
    
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

    try:
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX and 5XX status codes

        data = response.json()
        return data  # This will contain flight search results
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None