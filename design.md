Databases for API:

USERS: [ twitter_username | wallet ]

HISTORY: [ twitter_sender | twitter_reciever | amount | time | suceeded ]

PENDINGS: [ twitter_sender | twitter_reciever | amount | time ]  

- user writes tweet: "@ bot send <amount> to <username>"

- twitter bot (listens for the "@ bot" invokation):
    - if can't parse:
        - reply "failed invocation"
    - if can parse:
        - pass to Fulfilment API and await return code
    - Returncode processing:
        - if BROKE:
            - reply in thread "insuficcient funds"
        - if SUCCESS:
            - reply in thread "amount sent"
        - IF PENDING:
            - reply in thread "amount to be sent once registered"
            - DM recipient with signup process
        - if FAIL or no return code after 30s:
            - reply in thread "backend failure, will notify when sent"
            - add attempt to queue, retry top of queue every hour
                - when transactions get non-FAIL return code: process that code and remove from queue

- fulfilment API:
    - When recieve transaction:
    - IF sender does not have funds to send:
        - returncode: BROKE
    - IF recipient has address:
        - make transaction
        - add entry to HISTORY database
        - returncode: SUCCESS
    - ELIF recipient does not have wallet:
        - returncode: pending
        - add entry to PENDINGS database
    - ELSE:
        - returncode FAIL

- When new user registers:
    - SELECT * FROM pendings WHERE twitter_reciever = registered_name
    - for each transaction, send to fulfilment API and execute

- When user gets their history: (Via twitter DMs?)
    - SELECT * FROM history WHERE twitter_reciever = user getting history

- Every 20 days:
    - SELECT * FROM pendings WHERE (today()-time > 20days)
        - add to history database with suceeded=false, do not invoke fulfilment API
        - delete line from pendings