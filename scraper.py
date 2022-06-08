#chatBot
#By DracoRanger

import asyncio
from datetime import datetime
import unicodedata
import os
import requests
import time

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

already_running = False


for i in channel_id:
    num_channel_id.append((int(i)))

writeLocl = conf[3][:-1]

def clearBuffer(buffer, name):
    with open(name+'.txt', 'ab') as file:
        file.write(buffer)

def write_lines_to_file(buffer, name):

    attachements_already_scraped = False

    lines = bytes()
    lineNum = 0

    for message in buffer:
        lines = lines + (str(message.created_at.strftime("%d-%m-%Y")) + "# " + str(message.channel) + "- " + message.author.name + ": " + unicodedata.normalize('NFKD', message.content)+'\n\n').encode('UTF-8', 'ignore')
        if message.attachments and not attachements_already_scraped:
            for attachment in message.attachments:
                if not os.path.isfile(str(message.created_at.strftime("%d-%m-%Y")) + attachment.filename):
                    download = requests.get(attachment.url).content
                    with open(str(message.created_at.strftime("%d-%m-%Y")) + attachment.filename, 'wb') as handler:
                        handler.write(download)
        lineNum += 1
        if lineNum % 10000 == 0:
            clearBuffer(lines, name)
            lines = bytes()
    clearBuffer(lines, name)

async def scrape_data():

    global already_running

    already_running = True

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
    prev = 0
    for i in num_channel_id:
        if os.path.isfile(str(client.get_channel(i).name)+".txt") and prev != -1:
            print(f"Skipping {client.get_channel(i).name}")
            prev = i
        elif prev != -1 and prev != 0:
            print(f"Didn't find {client.get_channel(i).name}")
            channels.append(client.get_channel(prev))
            channels.append(client.get_channel(i))
            prev = -1
        else:
            print(f"Adding {client.get_channel(i).name}")
            channels.append(client.get_channel(i))


    data = []
    for channel in channels:
        data_temp = []
        try:
            print(f"Scraping {channel.name}")
            data_temp = await channel.history(limit = 2000000).flatten()
        except Exception as e:
                print('unable to access '+ channel.name)
                print('reason: '+str(e))
        data_temp.reverse()
        write_lines_to_file(data_temp, str(channel.name))
        print(f'{channel.name}->{len(data_temp)}')
        if data_temp:
            data.append(data_temp)
        time.sleep(30)

    messages_in_order = []
    curr_message_data = 0
    data_exists = True
    times_storage = [0]*len(data)
    messages_storage = [0]*len(data)

    print("->Merging sources in time order<-")

    for iter in range(0, len(data)):
        messages_storage[iter] = data[iter].pop(0)
        times_storage[iter] = messages_storage[iter].created_at

    print(f"Merge begins")

    counter = 0
    while data_exists:
        least_recent = min(times_storage)
        index = times_storage.index(least_recent)
        messages_in_order.append(messages_storage[index])
        
        if(data[index]):
            messages_storage[index] = data[index].pop(0)
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
        counter += 1
        
        if counter % 10000 == 0:
            write_lines_to_file(messages_in_order, writeLocl)
            messages_in_order = []

    

    write_lines_to_file(messages_in_order, writeLocl)

    already_running = False

@client.event
async def on_ready():
    global already_running

    print('Logged in as ' + client.user.name)
    print(str(datetime.now()))
    print('------')


    if not already_running:
        await scrape_data()
    else:
        while already_running:
            time.sleep(500)

    print('complete')
    input("Press enter to close, ignore all the error stuff that follows this")
    quit(1)

client.run(token)
