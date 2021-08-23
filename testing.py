import requests
import os
import tweepy as tw
import pandas as pd
import json


consumer_key= 'yourkeyhere'
consumer_secret= 'yourkeyhere'
access_token= 'yourkeyhere'
access_token_secret= 'yourkeyhere'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

# test authentication
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

#api.update_status("schmoney")

#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tw.StreamListener):

    def on_status(self, status):
        print(type(status))
        print(status.text)
        print(status._json['user']['screen_name'])
        parse_command(status)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

        # returning non-False reconnects the stream, with backoff.

myStreamListener = MyStreamListener()
myStream = tw.Stream(auth = api.auth, listener=myStreamListener)

#invocation phrase
myStream.filter(track=['tipjartest'], is_async=True)

def parse_command(content):
    sender = (content._json['user']['screen_name'])
    api.update_status("@"+ sender + " has got a lot to say ")