# ExpeditionExpertBot on Telegram

## Description

ExpeditionExpertBot is a Telegram bot designed to assist users in finding and booking flights. It provides real-time flight search functionality, allowing users to input their travel details and receive a list of best available flights matching their criteria. The bot retrieves flight information from a third-party flight search API and presents the results in a user-friendly format. 


## Link

https://t.me/ExpeditionExpertBot


## Libraries Used

1. Dotenv:  Reads api keys from .env file.
    
    ```bash
    pip install python-dotenv
    ```


2. pyTelegramBotAPI: Telegram bot api.

    ```bash
    pip install pyTelegramBotAPI
    ```


3. pycountry_convert: Converts country to ISO-3166-1 alpha-2 country code.

   ```bash
   pip install pycountry_convert
   ```
   

4. requests: Allows us to send http requests using Python.

   ```bash
   pip install requests
   ```


## APIs used

1. [Tequila Search API by Kiwi.com](https://tequila.kiwi.com/): returns the best flights
   


3. [Tequila Locations API by Kiwi.com](https://tequila.kiwi.com/): returns airport IATA codes of given city
   


## Hosting

We hosted our Telegram Bot on [PythonAnywhere](https://www.pythonanywhere.com/) by Anaconda. 
