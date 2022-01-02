import json
import requests
from requests import api
import os
from dotenv import load_dotenv


def fetch_translation(message=''):
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    translated_text = ""
    try:
        url = f"https://translation.googleapis.com/language/translate/v2?target=en&key={API_KEY}&q={message}"
        req = requests.get(url=url)
    except:
        print('network errror')


    response = json.loads(req.text) 
    try:
        translated_text = response.get('data').get('translations')[0].get('translatedText')
    except:
        print("api key error")

    return translated_text
