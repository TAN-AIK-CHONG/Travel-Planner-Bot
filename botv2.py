import os
from dotenv import load_dotenv
import telebot
from telebot import types
from search import kiwi_location_search, kiwi_flight_search
from datetime import datetime, timedelta
import pycountry_convert
import funcs
import json

# get bot token from env file (security practice)
load_dotenv(".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# initialise the bot
bot = telebot.TeleBot(BOT_TOKEN)

# initialise dictionary to store all concurrent user's and their inputs
users = {}

# country lists used to select partner_market
# l1 = countryList1, l2 = countryList2, l3 = countryList3
countryList = [[], [], []]
with open("countries1.txt", "r") as file:
    for row in file:
        countryList[0].append(row.rstrip())
with open("countries2.txt", "r") as file:
    for row in file:
        countryList[1].append(row.rstrip())
with open("countries3.txt", "r") as file:
    for row in file:
        countryList[2].append(row.rstrip())

# currencyList to store types of currency
currencyList = [[], []]
with open("currency1.txt", "r") as file:
    for row in file:
        currencyList[0].append(row.rstrip())
with open("currency2.txt", "r") as file:
    for row in file:
        currencyList[1].append(row.rstrip())

#currency flag file for flag emojis
with open('flags.json', 'r') as file:
    currency_flags = json.load(file)

# Initialise pages for InlineKBs
PAGE_country = 0
PAGE_curr = 0


# function to generate inline buttons (in message)
def generate_inline(bts_names, width):
    btn_list = []
    for buttons in bts_names:
        btn_list.append(types.InlineKeyboardButton(buttons, callback_data=buttons))
    markup = types.InlineKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup

def generate_currencies(bts_names, width):
    btn_list = []
    for buttons in bts_names:
        emoji = currency_flags[buttons]
        btn_list.append(types.InlineKeyboardButton(f"{emoji} {buttons}", callback_data=buttons))
    markup = types.InlineKeyboardMarkup(row_width=width)
    markup.add(*btn_list)
    return markup


# function to help check if user input is command. only used for ask_depart/ ask_return/ ask_date functions
def util_isCommand(message):
    command = message.text.split()[0]  # Extract the command
    if command == "/start" or command == "/settings":
        send_welcome(message)
    elif command == "/flights":
        check_type(message)
    else:
        bot.reply_to(
            message,
            "Sorry, I didn't understand that command. Please use /settings or /flights to begin",
        )
        send_welcome(message)


# -----------------------------BUTTON HANDLING FUNCTIONS-----------------------------#
def ctr_prev_next(callback):
    global PAGE_country
    if callback.data == "ctr_BUTTON_NEXT":
        PAGE_country += 1
    elif callback.data == "ctr_BUTTON_PREV":
        PAGE_country -= 1
    kb = generate_inline(countryList[PAGE_country], 3)
    if PAGE_country == 0:
        kb.add(types.InlineKeyboardButton(">", callback_data="ctr_BUTTON_NEXT"))
    elif PAGE_country == 1:
        btn_next = types.InlineKeyboardButton(">", callback_data="ctr_BUTTON_NEXT")
        btn_prev = types.InlineKeyboardButton("<", callback_data="ctr_BUTTON_PREV")
        kb.add(btn_prev, btn_next)
    elif PAGE_country == 2:
        btn_prev = types.InlineKeyboardButton("<", callback_data="ctr_BUTTON_PREV")
        kb.add(btn_prev)
    bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=kb,
    )


def curr_prev_next(callback):
    global PAGE_curr
    if callback.data == "curr_BUTTON_NEXT":
        PAGE_curr += 1
    elif callback.data == "curr_BUTTON_PREV":
        PAGE_curr -= 1
    kb = generate_currencies(currencyList[PAGE_curr], 4)
    if PAGE_curr == 0:
        kb.add(types.InlineKeyboardButton(">", callback_data="curr_BUTTON_NEXT"))
    elif PAGE_curr == 1:
        kb.add(types.InlineKeyboardButton("<", callback_data="curr_BUTTON_PREV"))
    bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=kb,
    )


def get_country_code(callback):
    chat_id = callback.message.chat.id
    users[chat_id]["flight_info"]["partner_market"] = (
        pycountry_convert.country_name_to_country_alpha2(callback.data)
    )
    bot.send_message(chat_id, f"Your selected country is: {callback.data}")
    currency_select(callback.message)


def get_currency(callback):
    chat_id = callback.message.chat.id
    users[chat_id]["flight_info"]["curr"] = callback.data
    bot.send_message(chat_id, f"Your selected currency is {callback.data}")
    check_type(callback.message)


def flight_type(callback):
    chat_id = callback.message.chat.id
    if callback.data == "TYPE_oneway":
        users[chat_id]["flight_info"]["return_state"] = 0
        flight(callback.message)
    elif callback.data == "TYPE_return":
        users[chat_id]["flight_info"]["return_state"] = 1
        flight(callback.message)


# <-------------------------------------MAIN BODY------------------------------------->#
@bot.message_handler(commands=["start", "settings"])
def send_welcome(message):
    chat_id = message.chat.id
    users[chat_id] = {}
    users[chat_id] = {"flight_info": {}}
    users[chat_id]
    bot.reply_to(
        message,
        "Hi, I'm ExpeditionExpertBot! I'll help you source cheap flights! Let's get started with your settings",
    )
    home_country(message)


def home_country(message):
    chat_id = message.chat.id
    global PAGE_country
    PAGE_country = 0
    kb1 = generate_inline(countryList[0], 3)
    btn_next = types.InlineKeyboardButton(">", callback_data="ctr_BUTTON_NEXT")
    kb1.add(btn_next)
    bot.send_message(chat_id, "Please select your home country:", reply_markup=kb1)


def currency_select(message):
    chat_id = message.chat.id
    global PAGE_curr
    PAGE_curr = 0
    kb = generate_currencies(currencyList[0], 4)
    btn_next = types.InlineKeyboardButton(">", callback_data="curr_BUTTON_NEXT")
    kb.add(btn_next)
    bot.send_message(chat_id, "Please choose your preferred currency \U0001F4B5", reply_markup=kb)


@bot.message_handler(commands=["flights"])
def check_type(message):
    chat_id = message.chat.id
    btn1 = types.InlineKeyboardButton("One-Way \u27A1", callback_data="TYPE_oneway")
    btn2 = types.InlineKeyboardButton("Return \U0001F501", callback_data="TYPE_return")
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(btn1, btn2)
    bot.send_message(
        chat_id,
        f"Hi, {message.chat.username}! \U0001F44B \n Let's get started. Choose a type of flight.",
        reply_markup=kb,
    )


def flight(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Which city are you departing from?")
    bot.register_next_step_handler(message, search_departure_city)


def search_departure_city(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    chat_id = message.chat.id
    term = message.text
    locale = "en-US"  # You can change this to the appropriate locale
    location_types = "airport"  # You can adjust the location types if needed
    limit = 10  # Number of search results to display
    active_only = True  # Whether to include only active locations

    # Perform location search
    search_results = kiwi_location_search(
        term, locale, location_types, limit, active_only
    )

    if search_results and search_results["results_retrieved"] > 0:
        # Create buttons for each search result
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for location in search_results["locations"]:
            button_text = f"{location['name']} ({location['code']})"
            markup.add(button_text)

        markup.add("Search again \U0001F50D")

        bot.send_message(
            chat_id, "Please select the departure city from the list below: \U00002B07", reply_markup=markup
        )
        bot.register_next_step_handler(message, select_departure_city)
    else:
        bot.reply_to(message, "No cities found. Please enter departure city again.")
        bot.register_next_step_handler(message, search_departure_city)


def select_departure_city(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    elif message.text == "Search again \U0001F50D":
        hide_markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, "Please enter a departure city.", reply_markup=hide_markup)
        bot.register_next_step_handler(message, search_departure_city)
        return
    chat_id = message.chat.id
    selected_city_text = message.text
    selected_city_name, selected_city_iata = selected_city_text.split(" (")
    selected_city_iata = selected_city_iata[:-1]  # Remove the closing parenthesis

    # Store selected city and its IATA code in user's flight info
    users[chat_id]["flight_info"]["fly_from"] = selected_city_name
    users[chat_id]["flight_info"]["fly_from_iata"] = selected_city_iata

    bot.reply_to(message, f"You've selected {selected_city_name}.")
    hide_markup = types.ReplyKeyboardRemove()
    bot.reply_to(message, "Which city are you arriving at?", reply_markup=hide_markup)
    bot.register_next_step_handler(message, search_arrival_city)


def search_arrival_city(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    chat_id = message.chat.id
    term = message.text
    locale = "en-US"  # You can change this to the appropriate locale
    location_types = "airport"  # You can adjust the location types if needed
    limit = 5  # Number of search results to display
    active_only = True  # Whether to include only active locations

    # Perform location search
    search_results = kiwi_location_search(
        term, locale, location_types, limit, active_only
    )

    if search_results and search_results["results_retrieved"] > 0:
        # Create buttons for each search result
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for location in search_results["locations"]:
            button_text = f"{location['name']} ({location['code']})"
            markup.add(button_text)

        markup.add("Search again \U0001F50D")

        bot.send_message(
            chat_id, "Please select the arrival city from the list below: \U00002B07", reply_markup=markup
        )
        bot.register_next_step_handler(message, select_arrival_city)
    else:   
        bot.reply_to(message, "No cities found. Please enter arrival city again.")
        bot.register_next_step_handler(message, search_arrival_city)


def select_arrival_city(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    elif message.text == "Search again \U0001F50D":
        hide_markup = hide_markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, "Please enter an arrival city.", reply_markup=hide_markup)
        bot.register_next_step_handler(message, search_arrival_city)
        return
    chat_id = message.chat.id
    selected_city_text = message.text
    selected_city_name, selected_city_iata = selected_city_text.split(" (")
    selected_city_iata = selected_city_iata[:-1]  # Remove the closing parenthesis

    # Store selected city and its IATA code in user's flight info
    users[chat_id]["flight_info"]["fly_to"] = selected_city_name
    users[chat_id]["flight_info"]["fly_to_iata"] = selected_city_iata

    bot.reply_to(message, f"You've selected {selected_city_name}.")
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(
        chat_id,
        "Please input the departure date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, ask_date)


def ask_date(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    print("ask date:", message.text)
    chat_id = message.chat.id
    date_format = "%d.%m.%Y"  # Date format to expect
    try:
        # Attempt to parse the received message as a date
        date = datetime.strptime(message.text, date_format).date()
        # If successful, proceed to the next step
        users[chat_id]["flight_info"]["date_from"] = message.text
        if users[chat_id]["flight_info"]["return_state"] == 0:
            users[chat_id]["flight_info"]["return_from"] = None
            flight_info = users[chat_id]["flight_info"]
            bot.reply_to(
                message,
                f"Confirm your details?\nHome Country: {flight_info['partner_market']}\nDeparture City: {flight_info['fly_from']}\nArrival City: {flight_info['fly_to']}\nFlight date: {flight_info['date_from']}\nReturn Date: {flight_info['return_from']}\nEnter 'confirm' to confirm, or any other input to restart",
            )
            bot.register_next_step_handler(message, confirmation)
        else:
            bot.reply_to(
                message, "When is the return flight? (Enter the date in DD.MM.YYYY)"
            )
            bot.register_next_step_handler(message, ask_return)
    except ValueError:
        # If the received message is not in the expected date format, ask again
        bot.reply_to(
            message,
            "Error! Please input the departure date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024",
        )
        print("message error input:", message.text)
        bot.register_next_step_handler(message, ask_date)


# ONLY IF RETURN FLIGHT, THEN EXECUTE
def ask_return(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    print("ask date:", message.text)
    chat_id = message.chat.id
    date_format = "%d.%m.%Y"  # Date format to expect
    try:
        # Attempt to parse the received message as a date
        date = datetime.strptime(message.text, date_format).date()
        # If successful, proceed to confirmation
        users[chat_id]["flight_info"]["return_from"] = message.text
        flight_info = users[chat_id]["flight_info"]
        bot.reply_to(
            message,
            f"Confirm your details?\nHome Country: {flight_info['partner_market']}\nDeparture City: {flight_info['fly_from']}\nArrival City: {flight_info['fly_to']}\nFlight date: {flight_info['date_from']}\nReturn Date: {flight_info['return_from']}\nEnter 'confirm' to confirm, or any other input to restart",
        )
        bot.register_next_step_handler(message, confirmation)
    except ValueError:
        # If the received message is not in the expected date format, ask again
        bot.reply_to(
            message,
            "Error! Please input the return date in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024",
        )
        print("message error input:", message.text)
        bot.register_next_step_handler(message, ask_return)


def confirmation(message):
    if message.text[0] == "/":
        util_isCommand(message)
        return
    print("confirmation message:", message.text)
    chat_id = message.chat.id
    confirmation_text = message.text.lower()

    if confirmation_text == "confirm":
        bot.send_message(
            chat_id,
            "Your flight details have been confirmed.\n"
            + "\U0001F50D Searching for best flights...",
        )
        search_flights(message)
    else:
        send_welcome(message)


def search_flights(message):
    chat_id = message.chat.id
    flight_info = users.get(chat_id, {}).get("flight_info")

    if flight_info:
        # Extract necessary information for flight search
        currency = flight_info.get("curr")
        partner_market = flight_info.get("partner_market")
        fly_from = flight_info.get("fly_from_iata")
        fly_to = flight_info.get("fly_to_iata")
        date_from_init = flight_info.get("date_from")
        return_from_init = flight_info.get("return_from")

        # Convert date format from DD.MM.YYYY to DD/MM/YYYY and subtract 1 day
        date_from = (
            datetime.strptime(date_from_init, "%d.%m.%Y") - timedelta(days=1)
        ).strftime("%d/%m/%Y")
        date_to = (
            datetime.strptime(date_from_init, "%d.%m.%Y") + timedelta(days=1)
        ).strftime("%d/%m/%Y")
        if return_from_init is None:
            return_to = None
            return_from = None
        else:
            return_to = (
                datetime.strptime(return_from_init, "%d.%m.%Y") + timedelta(days=1)
            ).strftime("%d/%m/%Y")
            return_from = (
                datetime.strptime(return_from_init, "%d.%m.%Y") - timedelta(days=1)
            ).strftime("%d/%m/%Y")

        # Perform flight search using the extracted information
        flight_search_results = kiwi_flight_search(
            fly_from,
            fly_to,
            date_from,
            date_to,
            return_from,
            return_to,
            partner_market,
            currency,
        )

        ##to be edited!!
        if flight_search_results:
            flights_info = []
            dispcurrency = flight_search_results["currency"]
            flight_search_results = flight_search_results.get("data", [])
            flight_search_results = flight_search_results[:5]
            for flight in flight_search_results:
                flight_info = funcs.extract_flight_info(flight)
                flights_info.append(flight_info)

            # Format the flight information for sending
            flight_message = "Here are some available flights:\n\n"
            for info in flights_info:
                flight_message += funcs.format_flight_info(info, dispcurrency)

            bot.send_message(chat_id, flight_message, parse_mode="HTML")
        else:
            bot.send_message(chat_id, "No flights found for the given criteria.")
    else:
        bot.send_message(chat_id, "Information not found. Please start a new search.")


# <-------------------------------------------MAIN BUTTON HANDLING FUNCTION---------------------------------->#
@bot.callback_query_handler(func=lambda call: True)
def btn_press_handler(callback):
    chat_id = callback.message.chat.id
    if callback.message:
        if callback.data.startswith("ctr_BUTTON_"):  # next_prev countries
            ctr_prev_next(callback)
        elif callback.data.startswith("curr_BUTTON_"):  # next_prev currency
            curr_prev_next(callback)
        elif (
            callback.data in countryList[0]
            or callback.data in countryList[1]
            or callback.data in countryList[2]
        ):  # for country setting button
            get_country_code(callback)
        elif (
            callback.data in currencyList[0] or callback.data in currencyList[1]
        ):  # for currency setting
            get_currency(callback)
        elif callback.data.startswith("TYPE_"):
            flight_type(callback)
    else:
        bot.send_message(chat_id, "An error occured. Please restart.\n /start")


bot.infinity_polling()
