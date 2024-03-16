import os
from dotenv import load_dotenv
import telebot
import requests

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')


bot = telebot.TeleBot(BOT_TOKEN)
flight_info = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, I'm ExpeditionExpertBot! I'll help you plan an itinerary for your vacation. /flight or /hotel to begin.")
    
@bot.message_handler(commands=['flight'])
def ask_origin(message):
    bot.reply_to(message, "What is your home country?")
    bot.register_next_step_handler(message, ask_depart)
    
def ask_depart(message):
    flight_info["partner_market"] = message.text
    bot.reply_to(message, "Which city is the flight departing from?")
    bot.register_next_step_handler(message, ask_arrive)
    
def ask_arrive(message):
    flight_info["fly_from"] = message.text
    bot.reply_to(message, "Which city does the flight arrive at?")
    bot.register_next_step_handler(message, ask_date)
    
def ask_date(message):
    flight_info["fly_to"] = message.text
    bot.reply_to(message, "Please input the date of the flight in DD.MM.YYYY format. eg. 24.04.2024 is 24 April 2024")
    bot.register_next_step_handler(message, ask_return)
    
def ask_return(message):
    flight_info["date_from"] = message.text
    bot.reply_to(message, "When is the return flight?")
    bot.register_next_step_handler(message, confirmation)

def confirmation(message):
    flight_info["return_from"] = message.text
    bot.reply_to(message, f"Confirm your details\nHome Country: {flight_info['partner_market']}\nDeparture City: {flight_info['fly_from']}\nArrival City: {flight_info['fly_to']}\nFlight date: {flight_info['date_from']}\nReturn Date: {flight_info['return_from']}")
    
        
bot.infinity_polling()  