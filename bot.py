import os
from dotenv import load_dotenv
import telebot
import requests
from telebot import types
from search import kiwi_location_search, kiwi_flight_search
from datetime import datetime, timedelta
import pycountry_convert

#get bot token from env file (security practice)
load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')

#initialise the bot
bot = telebot.TeleBot(BOT_TOKEN)

#initialise dictionary to store all concurrent user's and their inputs
users = {}

#country lists used to select partner_market
#i might change this to a list of lists
countryList1 = []
countryList2 = []
countryList3 = []
with open("countries1.txt", "r") as countryList:
    for row in countryList:
        countryList1.append(row.rstrip())

with open("countries2.txt", "r") as countryList:
    for row in countryList:
        countryList2.append(row.rstrip())
        
with open("countries3.txt", "r") as countryList:
    for row in countryList:
        countryList3.append(row.rstrip())

#function to generate keyboard buttons
def generate_buttons(bts_names,width):
    btn_list =[]
    for buttons in bts_names:
        btn_list.append(types.KeyboardButton(buttons))
    markup = types.ReplyKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup

#function to generate inline buttons (in text)
#specifially will generate buttons for country code
def generate_inline(bts_names,width):
    btn_list =[]
    for buttons in bts_names:
        btn_list.append(types.InlineKeyboardButton(buttons, callback_data=pycountry_convert.country_name_to_country_alpha2(buttons, cn_name_format="default")))
    markup = types.InlineKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = generate_buttons(['/flight','/hotel'],2)
    bot.reply_to(message, "Hi, I'm ExpeditionExpertBot! I'll help you source cheap flights and hotels. /flight or /hotel to begin.",
                 reply_markup=markup)
    
@bot.message_handler(commands=['flight'])
def ask_origin(message):
    #create user's ID
    chat_id = message.chat.id
    users[chat_id] = {"flight_info": {}}
    markup = generate_inline(countryList1, 3)
    bot.send_message(chat_id, "Please select your home country:", reply_markup=markup)
    
def ask_depart(message):
    bot.reply_to(message, "Which city is the flight departing from?")
    bot.register_next_step_handler(message, search_departure_city)

def search_departure_city(message):
    chat_id = message.chat.id
    term = message.text
    locale = "en-US"  # You can change this to the appropriate locale
    location_types = "airport"  # You can adjust the location types if needed
    limit = 10  # Number of search results to display
    active_only = True  # Whether to include only active locations

    # Perform location search
    search_results = kiwi_location_search(term, locale, location_types, limit, active_only)

    if search_results and search_results['results_retrieved'] > 0:
        # Create buttons for each search result
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for location in search_results['locations']:
            button_text = f"{location['name']} ({location['code']})"
            markup.add(button_text)

        bot.send_message(chat_id, "Please select the departure city:", reply_markup=markup)
        bot.register_next_step_handler(message, select_departure_city)
    else:
        bot.reply_to(message, "No cities found. Please enter departure city again.")
        bot.register_next_step_handler(message, search_departure_city)

def select_departure_city(message):
    chat_id = message.chat.id
    selected_city_text = message.text
    selected_city_name, selected_city_iata = selected_city_text.split(' (')
    selected_city_iata = selected_city_iata[:-1]  # Remove the closing parenthesis

    # Store selected city and its IATA code in user's flight info
    users[chat_id]["flight_info"]["fly_from"] = selected_city_name
    users[chat_id]["flight_info"]["fly_from_iata"] = selected_city_iata

    bot.reply_to(message, f"You've selected {selected_city_name}.")
    bot.reply_to(message, "Which city does the flight arrive at?")
    bot.register_next_step_handler(message, search_arrival_city)
    
def search_arrival_city(message):
    chat_id = message.chat.id
    term = message.text
    locale = "en-US"  # You can change this to the appropriate locale
    location_types = "airport"  # You can adjust the location types if needed
    limit = 5  # Number of search results to display
    active_only = True  # Whether to include only active locations

    # Perform location search
    search_results = kiwi_location_search(term, locale, location_types, limit, active_only)

    if search_results and search_results['results_retrieved'] > 0:
        # Create buttons for each search result
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for location in search_results['locations']:
            button_text = f"{location['name']} ({location['code']})"
            markup.add(button_text)

        bot.send_message(chat_id, "Please select the arrival city:", reply_markup=markup)
        bot.register_next_step_handler(message, select_arrival_city)
    else:
        bot.reply_to(message, "No cities found. Please enter arrival city again.")
        bot.register_next_step_handler(message, search_arrival_city)

def select_arrival_city(message):
    chat_id = message.chat.id
    selected_city_text = message.text
    selected_city_name, selected_city_iata = selected_city_text.split(' (')
    selected_city_iata = selected_city_iata[:-1]  # Remove the closing parenthesis

    # Store selected city and its IATA code in user's flight info
    users[chat_id]["flight_info"]["fly_to"] = selected_city_name
    users[chat_id]["flight_info"]["fly_to_iata"] = selected_city_iata

    bot.reply_to(message, f"You've selected {selected_city_name}.")
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Please input the departure date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024", reply_markup = markup)
    bot.register_next_step_handler(message, ask_date)
    
def ask_date(message):
    chat_id = message.chat.id
    date_format = "%d.%m.%Y"  # Date format to expect
    try:
        # Attempt to parse the received message as a date
        date = datetime.strptime(message.text, date_format).date()
        # If successful, proceed to the next step
        users[chat_id]["flight_info"]["date_from"] = message.text
        bot.reply_to(message, "When is the return flight? (Enter the date in DD.MM.YYYY)")
        bot.register_next_step_handler(message, ask_return)
    except ValueError:
        # If the received message is not in the expected date format, ask again
        bot.reply_to(message, "Error! Please input the departure date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024")
        bot.register_next_step_handler(message, ask_date)
    
def ask_return(message):
    chat_id = message.chat.id
    date_format = "%d.%m.%Y"  # Date format to expect
    try:
        # Attempt to parse the received message as a date
        date = datetime.strptime(message.text, date_format).date()
        # If successful, proceed to confirmation
        users[chat_id]["flight_info"]["return_from"] = message.text
        flight_info = users[chat_id]["flight_info"]
        bot.reply_to(message, f"Confirm your details?\nHome Country: {flight_info['partner_market']}\nDeparture City: {flight_info['fly_from']}\nArrival City: {flight_info['fly_to']}\nFlight date: {flight_info['date_from']}\nReturn Date: {flight_info['return_from']}\nEnter 'confirm' to confirm.")
        bot.register_next_step_handler(message, confirmation)
    except ValueError:
        # If the received message is not in the expected date format, ask again
        bot.reply_to(message, "Error! Please input the return date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024")
        bot.register_next_step_handler(message, ask_return)

def confirmation(message):
    chat_id = message.chat.id
    confirmation_text = message.text.lower()
    flight_info = users[chat_id]["flight_info"]

    if confirmation_text == 'confirm':
        confirmation_message = f"Your flight details have been confirmed:\n\n"
        confirmation_message += f"Home Country: {flight_info['partner_market']}\n"
        confirmation_message += f"Departure City: {flight_info['fly_from']}\n"
        confirmation_message += f"Arrival City: {flight_info['fly_to']}\n"
        confirmation_message += f"Flight date: {flight_info['date_from']}\n"
        confirmation_message += f"Return Date: {flight_info['return_from']}\n"
        confirmation_message += "\nThank you for confirming!"
        bot.send_message(chat_id, confirmation_message)
        bot.register_next_step_handler(message, search_flights)

def search_flights(message):
    chat_id = message.chat.id
    flight_info = users.get(chat_id, {}).get("flight_info")

    if flight_info:
        # Extract necessary information for flight search
        partner_market = flight_info.get("partner_market")
        fly_from = flight_info.get("fly_from_iata")
        fly_to = flight_info.get("fly_to_iata")
        date_from_init = flight_info.get("date_from")
        return_from_init = flight_info.get("return_from")

        # Convert date format from DD.MM.YYYY to DD/MM/YYYY and subtract 1 day
        date_from = (datetime.strptime(date_from_init, "%d.%m.%Y") - timedelta(days=1)).strftime("%d/%m/%Y")
        return_from = (datetime.strptime(return_from_init, "%d.%m.%Y") - timedelta(days=1)).strftime("%d/%m/%Y")
        date_to = (datetime.strptime(date_from_init, "%d.%m.%Y") + timedelta(days=1)).strftime("%d/%m/%Y")
        return_to = (datetime.strptime(return_from_init, "%d.%m.%Y") + timedelta(days=1)).strftime("%d/%m/%Y")

        # Perform flight search using the extracted information
        flight_search_results = kiwi_flight_search(fly_from, fly_to, date_from, date_to, return_from, return_to, partner_market)

        
        ##to be edited!!
        if flight_search_results:
            flights_info = []
            # Display the found flights to the user
            flight_message = "Here are some available flights:\n\n"
            for flight in flight_search_results:
                price = int(flight["price"])
                flight_info = {
                    "price": flight["price"],
                    "airline": flight["airlines"][0],  # Assuming there's only one airline per flight
                    "flight_number": flight["route"][0]["flight_no"],  # Taking the first flight number
                    "city_from": flight["cityFrom"],
                    "city_to": flight["cityTo"],
                    "return": flight["route"][0]["return"],
                    "fare_classes": flight["route"][0]["fare_classes"],
                }
                flights_info.append(flight_info)
                flight_message += f"Price: {flight_info['price']} {flight_info['airline']} {flight_info['flight_number']} {flight_info['city_from']} to {flight_info['city_to']} ({flight_info['fare_classes']})\n"

            bot.send_message(chat_id, flight_message)
        else:
            bot.send_message(chat_id, "No flights found for the given criteria.")
    else:
        bot.send_message(chat_id, "Information not found. Please start a new search.")

        
@bot.callback_query_handler(func=lambda call:True)
def get_country_code(callback):
    if callback.message: 
        #store user partner_country in flight_info
        chat_id = callback.message.chat.id
        users[chat_id]["flight_info"]["partner_market"] = callback.data
        bot.send_message(chat_id, f"Your selected country code is: {callback.data}")
        ask_depart(callback.message)
    else:
        bot.send_message(chat_id, "An error occured. Please restart.")
    

                

bot.infinity_polling()  