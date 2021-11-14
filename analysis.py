#chatBot
#By DracoRanger

import asyncio
from datetime import datetime
import unicodedata
import os

import discord
from discord.ext import commands

client = discord.Client()
bot = commands.Bot(command_prefix='!', description='')

config = open('botData.txt', 'r')
conf = config.readlines() #push to array or do directly
token = conf[0][:-1]
server_id = int(conf[1][:-1])
channel_id = int(conf[2][:-1])
writeLocl = conf[3][:-1]

def clearBuffer(buffer):
    with open(writeLocl+'.txt', 'a') as file:
        file.write(buffer.decode('ascii'))

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print(str(datetime.now()))
    print('------')

    authors = []
    started_conversation = []


    channel = client.get_channel(channel_id)

    print('Attempting ' + channel.name)
    try:
        messages = await channel.history(limit = 100000000).flatten()
        print('scraped '+channel.name)
    except Exception as e:
        print('unable to access '+ channel.name)
        print('reason: '+str(e))

    lineNum = 0
    lastTime = datetime(1970,1,1)
    for message in messages:
       if not message.author in authors:
           authors.append(message.author)
           started_conversation.append(0)
       else:
           c = message.created_at - lastTime
           if c.total_seconds() > 4*3600:
               for i in range(0,len(authors)):
                   if message.author == authors[i]:
                       started_conversation[i] = started_conversation[i] + 1

    print(authors)
    print(started_conversation)

    input("Press enter to close, ignore all the error stuff that follows this")
    quit(0)

client.run(token)
