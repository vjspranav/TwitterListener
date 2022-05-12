#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:11:52 2022

@author: vjspranav
"""
import json
import logging
import os
import telegram
import requests
import json
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler
import threading

with open('keys/config.json') as f:
    config = json.load(f)

token=config['TG_API']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = telegram.Bot(token=token)
print(bot.get_me())
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
QUERY='COMPUTER%20SCIENCE%20(DEGREE%20OR%20RESEARCH)'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Welcome to the Issue Bot")

def get_tweets_data():
    tweets=[]
    tweets_to_send=[]
    # Get local data from the file if it exists
    if os.path.isfile('data/tweets.json'):
        with open('data/tweets.json') as f:
            tweets = json.load(f)

    # Get all tweets containing the word "issue" and "oneplus" and "TV" and save it to the file
    # Use the search API to get the tweets V2
    url = 'https://api.twitter.com/2/tweets/search/recent?query=' + QUERY + '&tweet.fields=created_at&max_results=100'
    headers = {'Authorization': 'Bearer ' + config['TWITTER_API']}
    response = requests.get(url, headers=headers)
    print(response.status_code)
    # Add non existing tweets to the list
    for tweet in response.json()['data']:
        if tweet not in tweets:
            tweets_to_send.append(tweet)
    tweets.extend(response.json()['data'])
    # Remove duplicates
    # tweets = list(set(tweets))
    with open('data/tweets.json', 'w') as f:
         json.dump(tweets, f, indent=4)
    return tweets_to_send

def send_tweets(update, context):
    tweets_to_send = get_tweets_data()
    for tweet in tweets_to_send:
        # Send tweet url, tweet content and created_at
        msg='https://twitter.com/i/statuses/' + tweet['id']+'\n'+tweet['text']+'\n'+tweet['created_at']
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

functions = [start, send_tweets]
for function in functions:
    handler = CommandHandler(function.__name__, function)
    dispatcher.add_handler(handler)

def send_automatically():
    while True:
        tweets_to_send = get_tweets_data()
        for tweet in tweets_to_send:
            # Send tweet url, tweet content and created_at
            msg='https://twitter.com/i/statuses/' + tweet['id']+'\n'+tweet['text']+'\n'+tweet['created_at']
            bot.send_message(chat_id=config['TG_CHAT_ID'], text=msg)
        time.sleep(10)

def main():
    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    threading.Thread(target=send_automatically).start()
    main()
    # get_tweets_data()
    
