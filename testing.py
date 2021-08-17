import requests
import os
import tweepy as tw
import pandas as pd

consumer_key= 'yourkeyhere'
consumer_secret= 'yourkeyhere'
access_token= 'yourkeyhere'
access_token_secret= 'yourkeyhere'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

url = "https://api.twitter.com/1.1/statuses/update.json?status=schmoney"

x = requests.post(url)

print(x.text)