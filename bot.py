import os
from dotenv import load_dotenv
import telebot
from geopy.geocoders import GoogleV3

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

geolocator = GoogleV3(api_key=GOOGLE_API_KEY)

bot = telebot.TeleBot(BOT_TOKEN)
user_states ={}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hi, I'm ExpeditionExpertBot! I'll help you plan an itinerary for your vacation. /itinerary to begin.")
    
@bot.message_handler(commands=['itinerary'])
def ask_city(message):
    bot.reply_to(message, "Which city are you planning on visiting?")
    bot.register_next_step_handler(message, process_location)
    
def process_location(message):
    city_name = message.text
    location = geolocator.geocode(city_name)
    latitude = location.latitude
    longitude = location.longitude
    bot.send_message(message.from_user.id, f"The location latitude is {latitude} and the location longitude is {longitude}")
        
bot.infinity_polling()  