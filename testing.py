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

def get_wallet_balance(wal):
    with open("balances.txt", "r") as f:
        f = f.read().splitlines()
    for l in f:
        l = l.split(":")
        if int(l[0]) == wal:
            return int(l[1])
    return -1
    
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
    p1 = [pretty_transaction(e) for e in h]
    p2 = "\n".join(p1)
    print("here")
    api.update_status(status=(p2), in_reply_to_status_id = content._json["id"])
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

#transactions to senders not yet registered are denoted as failed after <20 days>
def prune_pendings():
    goods = []
    fails = []
    cur = time.time()
    with open ("pendings.txt") as f:
        f = f.read().splitlines()
    for e in f:
        e_split = e.split(":")
        age = cur - int(e_split[3])
        if age > (60 * 60 * 24 * 20):
            fails.append(e)
        else:
            goods.append(e)

    #write mode clears the file to start - intended
    with open ("pendings.txt", "w") as p:
        for e in goods:
            p.write(e+"\n")
    p.close()

    #will want to insert these in in order in the future
    with open ("history.txt", "a") as h:
        for e in fails:
            h.write(e + ":False")
    h.close()

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

def debit_wallet(wal, amount):
    with open("balances.txt") as w:
        lines = w.read().splitlines()
    for c, each in enumerate(lines):
        e = each.split(":")
        if int(e[0]) == wal:
            b = int(e[1]) + amount
            e[1] = str(b)
        lines[c] = ":".join(e)
    w.close()
    with open ("balances.txt", "w") as w:
        for e in lines:
            w.write(e + "\n")
    w.close()
    return

def transaction(sender, recipient, amount):
    from_w = get_user_wallet(sender)
    to_w = get_user_wallet(recipient)
    debit_wallet(from_w, -amount)
    debit_wallet(to_w, amount)
    txn = [sender, recipient, str(amount), str(int(time.time())), "True"]
    txn = ":".join(txn)
    with open("history.txt", "a") as h:
        h.write(txn + "\n")
    return

#expected format: (@tipjartest send 10 to mitch)
def create_transaction(content):
    sender = (content._json['user']['screen_name'])
    id = (content._json['id'])
    tweet = content._json["text"].split(" ")
    
    #expected format: (@tipjartest send 10 to mitch)
    val = int(tweet[2])
    recipient = tweet[4]
    
    if (get_wallet_balance(get_user_wallet(sender)) < val):
        api.update_status("ERROR: Insufficient funds to initiate transaction", in_reply_to_status_id = id)
    elif (val < 0):
        api.update_status("ERROR: No negative value transactions", in_reply_to_status_id = id)
    elif not (user_is_registered(recipient)):
        transact = ":".join([sender, recipient, str(val), str(int(time.time()))])
        f = open("pendings.txt", "a")
        f.write(transact + "\n")
        f.close()
        transact = transact + "Sending" + str(val) + " to " + recipient + " [Pending recipient registration]"
        api.update_status(status=(transact), in_reply_to_status_id = id)
    else:
        transaction(sender, recipient, val)
        msg = "Sent " + str(val) + " to " + recipient
        api.update_status(status = msg, in_reply_to_status_id = id)
    return 
