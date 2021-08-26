import requests
import os
import tweepy as tw
import pandas as pd
import json
import time

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


#Handles reading of bot mentions
def parse_command(content):
    sender = (content._json['user']['screen_name'])
    id = (content._json['id'])
    tweet = content._json["text"].split(" ")
    
    #expected format: (@tipjartest send 10 to mitch)
    #this is not verified yet; improper commands will crash me, plz be nice
    val = int(tweet[2])
    recipient = tweet[4]
    transact = ":".join([sender, recipient, str(val), str(time.time())])

    api.update_status(status=(transact), in_reply_to_status_id = id) 

def get_user_wallet(user):
    with open("wallets.txt", "r") as f:
        f = f.read().splitlines()
    for l in f:
        l = l.split(":")
        print(l)
        if l[0] == user:
            return int(l[1])
    return -1

def get_user_history(user):
    hists = []
    with open("history.txt") as f:
        f = f.read().splitlines()
    for l in f:
        parts = l.split(":")
        if parts[0] == user or parts[1] == user:
            hists.append(l)
    return hists