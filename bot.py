import os
from dotenv import load_dotenv
import telebot

load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hi, I'm ExpeditionExpertBot! Here's what I can do:")
    
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
    
bot.infinity_polling()