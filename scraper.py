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

#TODO reverse logic, since it appears that lastmessage is the newer message
@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print(str(datetime.now()))
    print('------')

    lines = bytes()
    messages = []

    try:
        f = open(writeLocl+'.txt')
        f.close()
        os.remove(writeLocl+'.txt')
    except IOError:
        pass
    finally:
        f = open(writeLocl+'.txt', "x")
        f.close()

    channel = client.get_channel(channel_id)

    print('Attempting ' + channel.name)
    try:
        messages = await channel.history(limit = 100000).flatten()
        print('scraped '+channel.name)
    except Exception as e:
        print('unable to access '+ channel.name)
        print('reason: '+str(e))

    lineNum = 0
    for message in reversed(messages):
        #lines = lines + (message.author.name + unicodedata.normalize('NFKD', message.content).replace('\n', ' ').replace('\r','')+'\n').encode('ascii', 'ignore')
        lines = lines + (message.author.name + ": " + unicodedata.normalize('NFKD', message.content)+'\n\n').encode('ascii', 'ignore')
        if lineNum % 5000 == 0:
            clearBuffer(lines)
            lines = bytes()
    print('complete')

    input("Press enter to close, ignore all the error stuff that follows this")
    quit(1)

client.run(token)
