from sys import path
import requests
import os
import tweepy as tw
import pandas as pd
import json
import time
import datetime
from pathlib import Path

with open(Path("../keys.txt")) as s:
    s = s.read().splitlines()
consumer_key= s[0]
consumer_secret= s[1]
access_token= s[2]
access_token_secret= s[3]


auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

# test authentication
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

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
myStream.filter(track=['tipjartest'], is_async=True) #invocation phrase

#expected format: (@tipjartest send 10 to mitch)
def create_transaction(content):
    sender = (content._json['user']['screen_name'])
    id = (content._json['id'])
    tweet = content._json["text"].split(" ")
    
    #expected format: (@tipjartest send 10 to mitch)
    val = int(tweet[2])
    recipient = tweet[4]
    transact = ":".join([sender, recipient, str(val), str(time.time())])
    f = open("pendings.txt", "a")
    f.write(transact + "\n")
    f.close()
    api.update_status(status=(transact), in_reply_to_status_id = id) 
    return 

#Handles all bot mentions - guides to proper methods
def parse_command(content):
    sender = (content._json['user']['screen_name'])
    id = (content._json['id'])
    tweet = content._json["text"].split(" ")
    verb = tweet[1]

    if verb == "send":
        create_transaction(content)
    if verb == "balance":
        show_balance(content)
    if verb == "history":
        show_history(content)
    return

def show_history(content):
    h = get_user_history(content._json["user"]["screen_name"])
    pretties = [pretty_transaction(e) for e in h]
    api.update_status(status=(pretties), in_reply_to_status_id = content._json["id"])
    return

#nicely format transactions in strin
def pretty_transaction(txn):
    txn = txn.split(":")
    t = str(datetime.datetime.fromtimestamp(int(txn[3])))
    s = t + ": " + txn[0] + " sent " + txn[2] + " to " + txn[1]
    if bool(txn[3]) == False:
        s = s + " - Failed due to recipient registration timeout"
    return s

#replies to "balance" query
def show_balance(content):
    user = content._json["user"]["screen_name"]
    if user_is_registered(user):
        wal = get_user_wallet(user)
        bal = get_wallet_balance(wal)
        id = content._json["id"]
        api.update_status(status=("Balance of " + user + " is " + str(bal)), in_reply_to_status_id = id)
    return

def user_is_registered(user):
    return (get_user_wallet(user) != -1)

def get_user_wallet(user):
    with open("wallets.txt", "r") as f:
        f = f.read().splitlines()
    for l in f:
        l = l.split(":")
        if l[0] == user:
            return int(l[1])
    return -1

def get_wallet_balance(wal):
    with open("balances.txt", "r") as f:
        f = f.read().splitlines()
    for l in f:
        l = l.split(":")
        if int(l[0]) == wal:
            return int(l[1])
    return -1

#transactions to senders not yet registered are denoted as failed after <20 days>
def prune_pendings():
    return

#get the last <count> transactions to or from a user
def get_user_history(user, count=3):
    hists = []
    with open("history.txt") as f:
        f = f.read().splitlines()
    for l in f:
        parts = l.split(":")
        if parts[0] == user or parts[1] == user:
            hists.append(l)
        if len(hists) >= count:
            break
    return hists