# bot.py
import os
import pandas as pd
import random
import discord

from datetime import datetime, timezone, time
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

## Set the time for the message task to run each date
## Currently set to 10AM Eastern Time (2PM UTC Time)
utc = timezone.utc
runtime = time(hour=14, minute=0, tzinfo=utc)

def get_holiday():
    ## Select a random holiday from holidays.json for today's date
    holidays_df = pd.read_json('holidays.json')
    today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
    holidays_df = holidays_df.loc[holidays_df['Date'] == today]
    holiday_row = holidays_df.sample()
    holiday_name = holiday_row['Holiday'].item()
    holiday_link = holiday_row['Link'].item()

    return holiday_name, holiday_link

def get_random_member(server_input):
    ## Select a member of the server at random and make sure member is not a bot
    member = random.choice(server_input.guild.members)
    while member.bot == True:
        member = random.choice(server_input.guild.members)
    return member

def get_messages(holiday_name: str, holiday_link, member):
    ## Create messages/embeds that the bot will send out
    response1 = f'🎉🎉🎉 Time to celebrate! Today is {holiday_name}! 🎉🎉🎉'
    embed = discord.Embed(title=holiday_name,
                          url=holiday_link
                        )
    embed.url = holiday_link
    response2 = f'{member.mention} let everyone know how you\'re celebrating {holiday_name}!'
    return response1, embed, response2

## Run CelebrationBot message with !celebrate command
@bot.command(name='celebrate')
async def my_command(ctx):
    
    holiday_name, holiday_link = get_holiday()
    member = get_random_member(ctx)
    response1, embed, response2 = get_messages(holiday_name,holiday_link,member)

    await ctx.send(response1)
    await ctx.send(embed=embed)
    await ctx.send(response2)

## Run CelebrationBot message at 10:00AM Eastern time every day
@tasks.loop(time=runtime)
async def my_task():
    print("My task is running!")
    holiday_name, holiday_link = get_holiday()
    ## Get the channel that the bot messages will be sent to
    ## Defaults to first channel in the server
    text_channel_list = []
    for server in bot.guilds:
        for channel in server.channels:
            if str(channel.type) == 'text':
                text_channel_list.append(channel)
    channel = text_channel_list.pop(0)
    print(channel)
    
    member = get_random_member(channel)
    print(member)
    
    response1, embed, response2 = get_messages(holiday_name,holiday_link,member)
    await channel.send(response1)
    await channel.send(embed=embed)
    await channel.send(response2)

## Run CelebrationBot message on bot startup
@bot.event
async def on_ready():
    ## Start the my_task loop run first
    my_task.start()
    ## Run CelebrationBot message next
    holiday_name, holiday_link = get_holiday()

    ## Get the channel that the bot messages will be sent to
    ## Defaults to first channel in the server
    text_channel_list = []
    for server in bot.guilds:
        for channel in server.channels:
            if str(channel.type) == 'text':
                text_channel_list.append(channel)
    channel = text_channel_list.pop(0)
    print(channel)

    member = get_random_member(channel)
    print(member)
    
    response1, embed, response2 = get_messages(holiday_name,holiday_link,member)
    await channel.send(response1)
    await channel.send(embed=embed)
    await channel.send(response2)

bot.run(TOKEN)