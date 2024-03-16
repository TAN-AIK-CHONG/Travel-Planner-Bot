import os
from dotenv import load_dotenv
import telebot
from flask import Flask, request,  jsonify, render_template
import requests

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEOFINDER_KEY = os.getenv('GEOFINDER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
user_states ={}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hi, I'm ExpeditionExpertBot! I'll help you plan an itinerary for your vacation. /itinerary to begin.")
    
@bot.message_handler(commands=['itinerary'])
def ask_city(message):
    user_states[message.chat.id] = 'waiting_for_city'
    bot.reply_to(message, "Which city are you planning on visiting?")
    
@bot.message_handler(content_types=['location'], func=lambda message: user_states.get(message.chat.id) == 'waiting_for_city')
def process_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    del user_states[message.chat.id]  # Remove the user state
    bot.reply_to(message, f"The location latitude is {latitude} and the location longitude is {longitude}")
        
bot.infinity_polling()