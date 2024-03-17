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
    deep_link = flight["deep_link"]
    price = flight["price"]
    departure_duration = flight["duration"]["departure"] // 60 // 60
    return_duration = flight["duration"]["departure"] // 60 // 60
    local_departure = datetime.strptime(flight["local_departure"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
    local_arrival = datetime.strptime(flight["local_arrival"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y, %H:%M")
    airline = flight["airlines"][0]  # Assuming there's only one airline per flight
    route = flight["route"]

    

    return {
        "deep_link": deep_link,
        "price": price,
        "departure_duration": departure_duration,
        "return_duration": return_duration,
        "local_departure": local_departure,
        "local_arrival": local_arrival,
        "airline": airline,
    }

def format_flight_info(info):
    flight_message = ""
    flight_message += f"Price: EUR {info['price']}, Airline: {info['airline']}\n"
    flight_message += f"Departure: {info['local_departure']}, Arrival: {info['local_arrival']}\n"
    flight_message += f"Departure Duration: {info['departure_duration']}h\n"
    flight_message += f"Return Duration: {info['return_duration']}h\n\n"

    flight_message += f"<a href='{info['deep_link']}'>More Details/Book</a>\n\n\n"

    return flight_message