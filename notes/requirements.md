Service will allow any Twitter user to send BSV to any recipient on Twitter user through their @ name without requiring the recipient to provide a wallet address.
Example: @service send $1 to @recipient

The Service will check to see if Sender has enough value in their wallet on the system to complete the transaction (value sent + estimated network transaction fee).

If Sender has enough value, the Service will check to see if Recipient has a wallet address on the system.

If Recipient does not have a wallet, the Service will put the transaction into a Pending Registration status, and send two notifications to the Recipient on Twitter.

Notification 1 will occur in thread of message where @service was mentioned.
Example: Hey! @recipient you have received $1 from @sender.

Notification 2 will occur as a direct tweet to @recipient.
Example: @recipient you have received BSV. Respond with !register to collect.

If the Recipient fails to register within 20 days, the transaction status will change to Registration Failure, and transaction will no longer be valid to complete. The value from Sender should still be in the Sender's wallet since we never were able to execute the transaction.

If Recipient is registered, the Service will send the value to Recipient's derived wallet address, and notify the Recipient on Twitter about the transaction. Transaction status will change to Completed and add a transaction hash from the network in the transaction table.

Notification will occur in thread of message where @service was mentioned.
Example: Hey! @recipient you have received $1 from @sender.

If we are unable to complete the transaction due to network connection failure. We should capture that error as a transaction status Network Failure. This will tell the system to retry these transaction once network connection is restored.