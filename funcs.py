from datetime import datetime, timedelta
from telebot import types
import pycountry_convert

#function to generate inline buttons (in text)
#specifially will generate buttons for country code
def generate_inline(bts_names,width):
    btn_list =[]
    for buttons in bts_names:
        btn_list.append(types.InlineKeyboardButton(buttons, callback_data=pycountry_convert.country_name_to_country_alpha2(buttons, cn_name_format="default")))
    markup = types.InlineKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup


#function to generate keyboard buttons
def generate_buttons(bts_names,width):
    btn_list =[]
    for buttons in bts_names:
        btn_list.append(types.KeyboardButton(buttons))
    markup = types.ReplyKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup

def extract_flight_info(flight):
    # Extract necessary information from the flight
    fly_from = flight["flyFrom"]
    fly_to = flight["flyTo"]
    city_from = flight["cityFrom"]
    city_to = flight["cityTo"]
    deep_link = flight["deep_link"]
    price = flight["price"]
    local_departure = datetime.strptime(flight["local_departure"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
    local_arrival = datetime.strptime(flight["local_arrival"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
    airline = flight["airlines"][0]  # Assuming there's only one airline per flight
    route = flight["route"]
    return_departure = None
    onward_stops = -1
    return_stops = -1
    for segment in route:
        if segment["return"] == 0:
            if segment["flyFrom"] != fly_from or segment["flyTo"] != fly_to:
                onward_stops += 1
        elif segment["return"] == 1:
            if return_departure is None:
                return_departure = datetime.strptime(segment["local_departure"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
            return_arrival = datetime.strptime(segment["local_arrival"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
            if segment["flyFrom"] != fly_from or segment['flyTo'] != fly_to:
                return_stops += 1

    return {
        "fly_from": fly_from,
        "fly_to": fly_to,
        "city_from": city_from,
        "city_to": city_to,
        "deep_link": deep_link,
        "price": price,
        "local_departure": local_departure,
        "local_arrival": local_arrival,
        "return_departure": return_departure,
        "return_arrival": return_arrival,
        "onward_stops": onward_stops,
        "return_stops": return_stops,
        "airline": airline,
    }

def format_flight_info(info):
    flight_message = ""
    flight_message += f"<b>{info['city_from']} ({info['fly_from']}) - {info['city_to']} ({info['fly_to']})</b>\n"
    if info['onward_stops'] < 1:
        flight_message += "\U0001F504 Direct\n"
    else:
        flight_message += f"\U0001F504 Stops: {info['onward_stops']}\n"
    flight_message += f"\U0001F6EB Departure: {info['local_departure']}\n"
    flight_message += f"\U0001F6EC Arrival: {info['local_arrival']}\n\n"
    flight_message += f"<b>{info['city_to']} ({info['fly_to']}) - {info['city_from']} ({info['fly_from']})</b>\n"
    if info['return_stops'] < 1:
        flight_message += "\U0001F504 Direct\n"
    else:
        flight_message += f"\U0001F504 Stops: {info['return_stops']}\n"
    flight_message += f"\U0001F6EB Departure: {info['return_departure']}\n"
    flight_message += f"\U0001F6EC Arrival: {info['return_arrival']}\n\n"
    flight_message += f"Price: EUR {info['price']}, Airline: {info['airline']}\n"
    flight_message += f"\U0001F517 <a href='{info['deep_link']}'>More Details/Book</a>\n"
    flight_message += "_____________________________\n\n"

    return flight_message