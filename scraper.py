#chatBot
#By DracoRanger

import asyncio
from datetime import datetime
import unicodedata
import os
import requests

import discord
from discord.ext import commands

client = discord.Client()
bot = commands.Bot(command_prefix='!', description='')

config = open('botData.txt', 'r')
conf = config.readlines() 
token = conf[0][:-1]
server_id = int(conf[1][:-1])
channel_id = conf[2][:-1].split(",")
num_channel_id = []

for i in channel_id:
    num_channel_id.append((int(i)))

writeLocl = conf[3][:-1]

def clearBuffer(buffer):
    with open(writeLocl+'.txt', 'ab') as file:
        file.write(buffer)

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

    channels = []
    for i in num_channel_id:
        channels.append(client.get_channel(i))

    data = []
    for channel in channels:
        try:
            print(f"Scraping {channel.name}")
            data.append(await channel.history(limit = 10).flatten())
        except Exception as e:
                print('unable to access '+ channel.name)
                print('reason: '+str(e))

    messages_in_order = []
    curr_message_data = 0
    data_exists = True
    times_storage = [0]*len(data)
    messages_storage = [0]*len(data)

    for iter in range(0, len(data)):
        messages_storage[iter] = data[iter].pop()
        times_storage[iter] = messages_storage[iter].created_at

    print(times_storage)

    while data_exists:
        most_recent = min(times_storage)
        index = times_storage.index(most_recent)
        messages_in_order.append(messages_storage[index])
        
        if(data[index]):
            messages_storage[index] = data[index].pop()
            times_storage[index] = messages_storage[index].created_at
        else:
            messages_storage[index] = 0
            times_storage[index] = datetime.now()

            finished = True
            for i in messages_storage:
                if i != 0:
                    finished = False
            if finished:
                data_exists = False
                break 

    output = []
    lineNum = 0
    most_recent = 0
    for message in messages_in_order:
        print(message.channel)
        lines = lines + (str(message.created_at.strftime("%d-%m-%Y")) + "# " + str(message.channel) + "- " + message.author.name + ": " + unicodedata.normalize('NFKD', message.content)+'\n\n').encode('UTF-8', 'ignore')
        if(message.attachments):
            for attachment in message.attachments:
                download = requests.get(attachment.url).content
                with open(str(message.created_at.strftime("%d-%m-%Y")) + attachment.filename, 'wb') as handler:
                    handler.write(download)
        lineNum += 1
        if lineNum % 10000 == 0:
            clearBuffer(lines)
            lines = bytes()
    clearBuffer(lines)
    print('complete')
    input("Press enter to close, ignore all the error stuff that follows this")
    quit(0)

client.run(token)
