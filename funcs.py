from datetime import datetime, timedelta

def extract_flight_info(flight):
    # Extract necessary information from the flight
    deep_link = flight["deep_link"]
    price = flight["price"]
    departure_duration = flight["duration"]["departure"] // 60 // 60
    return_duration = flight["duration"]["departure"] // 60 // 60
    local_departure = datetime.strptime(flight["local_departure"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
    local_arrival = datetime.strptime(flight["local_arrival"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
    airline = flight["airlines"][0]  # Assuming there's only one airline per flight
    route = flight["route"]

    # Extract information about each route segment
    route_info = []
    for segment in route:
        route_info.append({
            "fly_from": segment["cityFrom"],
            "fly_to": segment["cityTo"],
            "departure": datetime.strptime(segment["local_departure"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M"),
            "arrival": datetime.strptime(segment["local_arrival"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M"),
            "flight_number": segment["flight_no"],
            "airline": segment["airline"]
        })

    return {
        "deep_link": deep_link,
        "price": price,
        "departure_duration": departure_duration,
        "return_duration": return_duration,
        "local_departure": local_departure,
        "local_arrival": local_arrival,
        "airline": airline,
        "route_info": route_info
    }

def format_flight_info(info):
    flight_message = ""
    flight_message += f"Price: EUR {info['price']}, Airline: {info['airline']}\n"
    flight_message += f"Departure: {info['local_departure']}, Arrival: {info['local_arrival']}\n"
    flight_message += f"Departure Duration: {info['departure_duration']}h\n"
    flight_message += f"Return Duration: {info['return_duration']}h\n\n"
        
    # Add information about all transiting flights
    flight_message += "Flight Route:\n"
    for segment in info['route_info']:
        flight_message += f"Flight {segment['flight_number']} from {segment['fly_from']} to {segment['fly_to']}\n"
        flight_message += f"Departure: {segment['departure']}, Arrival: {segment['arrival']}\n"
        flight_message += f"Airline: {segment['airline']}\n\n"


    flight_message += f"<a href='{info['deep_link']}'>More Details/Book</a>\n\n\n"

    return flight_message