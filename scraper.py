# chatBot
# By DracoRanger

import asyncio
import os
import json
import time

import discord

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

config = open('botData.txt', 'r')
conf = config.readlines()
token = conf[0][:-1]
server_id = int(conf[1][:-1])

content_file = "./scraped/"


def write_data_to_file(buffer, name):
    '''
    Tries to handle dumping json dumping to file
    '''

    global content_file

    def default(o):
        del o
        return " "

    with open(f"{content_file}{name}.json", "w+", encoding="UTF-8") as file:
        file.write(json.dumps(obj=buffer, indent=4,
                   default=default, sort_keys=True))

    return


async def scrape_data(channel):
    '''
    This iterates through the channel and scrapes the data
    '''
    global content_file

    data = {}
    try:
        print(f"Scraping {channel.name}")
        data_temp = channel.history(limit=None)
    except Exception as e:
        print('unable to access ' + channel.name)
        print('reason: '+str(e))

    async for message in data_temp:
        data[f"{message.created_at}"] = {
            "author": message.author.display_name,
            "author_id": message.author.name,
            "content": message.content
        }
        if message.attachments:

            for attachment in message.attachments:
                if not os.path.isfile(f"{content_file}{channel.name}_{attachment.id}_{attachment.filename}.json"):
                    await attachment.save(f"{content_file}{channel.name}_{attachment.id}_{attachment.filename}.json")

    return data


async def scrape_channels(channels):
    '''
    This iterates through the channels and prompts scraping
    '''

    global client

    for channel in client.get_all_channels():
        if isinstance(channel, discord.CategoryChannel):
            continue     
        if not os.path.isfile(f"./{content_file}{channel.name}.json"):
            channels.append((channel))

    data = {}

    for channel in channels:

        result = await scrape_data(channel)

        data[channel.name] = result

        write_data_to_file(data[channel.name], channel.name)

        time.sleep(5)


@client.event
async def on_ready():

    print(f'Logged in as {client.user.name}')
    print('------')

    channels = []

    await scrape_channels(channels)

    print('complete')
    exit(0)

client.run(token)
