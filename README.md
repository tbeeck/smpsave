# Dynamic Private Game Server Provisioner
Save money hosting private game servers for you and your friends.

## Objective
Many groups of gamers wish to have dedicated, private servers to play with their friends, but this costs money.
At the time of writing, linode charges ~$48 USD per month for a server powerful enough to play modded minecraft, billed hourly.
However, most people who play as a group tend to only play as a group, for a few hours at a time. 
If you play 10 hours a week with friends, this would amount to `10 hours * $0.072 /hours * 4 weeks/month = $2.88` of actual usage per month. 
So why pay almost $50?

Manually turning the server on/off as needed creates two problems:
1. The person 'in charge' of the server needs to be available to turn it on/off.
2. Many hosts won't save the data on your server, meaning you need to back it up yourself (or pay for backups).


This project aims to solve problems 1 and 2 above by:
1. Providing a common interface that any authorized person can use to set up / tear down the server, via a discord bot.
2. Providing a mechanism to upload/download your server files upon the setup and tear down steps, so you keep your progress and can easily configure the server to your liking.
