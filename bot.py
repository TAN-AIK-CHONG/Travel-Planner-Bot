import os
from dotenv import load_dotenv
import telebot
import requests
from telebot import types
from search import kiwi_location_search
import datetime

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
users = {}

#country lists used to select partner_market
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

def generate_buttons(bts_names,width):
    btn_list =[]
    for buttons in bts_names:
        btn_list.append(types.KeyboardButton(buttons))
    markup = types.ReplyKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup

def generate_inline(bts_names,width):
    btn_list =[]
    for buttons in bts_names:
        btn_list.append(types.InlineKeyboardButton(buttons, url='abc.com'))
    markup = types.InlineKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = generate_buttons(['/flight','/hotel'],2)
    bot.reply_to(message, "Hi, I'm ExpeditionExpertBot! I'll help you plan an itinerary for your vacation. /flight or /hotel to begin.",
                 reply_markup=markup)
    
@bot.message_handler(commands=['flight'])
def ask_origin(message):
    chat_id = message.chat.id
    users[chat_id] = {"flight_info": {}}
    markup = generate_inline(countryList1, 3)
    bot.send_message(chat_id, "Please select your home country:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_depart)
    
def ask_depart(message):
    chat_id = message.chat.id
    users[chat_id]["flight_info"]["partner_market"] = message.text
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

    if search_results and 'locations' in search_results:
        # Create buttons for each search result
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for location in search_results['locations']:
            button_text = f"{location['name']} ({location['code']})"
            markup.add(button_text)

        bot.reply_to(message, "Please select the departure city:", reply_markup=markup)
        bot.register_next_step_handler(message, select_departure_city)
    else:
        bot.reply_to(message, "No cities found. Please try again.")

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

    if search_results and 'locations' in search_results:
        # Create buttons for each search result
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for location in search_results['locations']:
            button_text = f"{location['name']} ({location['code']})"
            markup.add(button_text)

        bot.reply_to(message, "Please select the arrival city:", reply_markup=markup)
        bot.register_next_step_handler(message, select_arrival_city)
    else:
        bot.reply_to(message, "No cities found. Please try again.")

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
    bot.reply_to(message, "Please input the departure date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024")
    bot.register_next_step_handler(message, ask_date)
    
def ask_date(message):
    chat_id = message.chat.id
    date_format = "%d.%m.%Y"  # Date format to expect
    try:
        # Attempt to parse the received message as a date
        date = datetime.datetime.strptime(message.text, date_format).date()
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
        date = datetime.datetime.strptime(message.text, date_format).date()
        # If successful, proceed to confirmation
        users[chat_id]["flight_info"]["return_from"] = message.text
        flight_info = users[chat_id]["flight_info"]
        bot.reply_to(message, f"Confirm your details\nHome Country: {flight_info['partner_market']}\nDeparture City: {flight_info['fly_from']}\nArrival City: {flight_info['fly_to']}\nFlight date: {flight_info['date_from']}\nReturn Date: {flight_info['return_from']}")
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
        
@bot.callback_query_handler(function=lambda call:True)
def 
    
bot.infinity_polling()  