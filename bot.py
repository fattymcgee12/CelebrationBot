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
holiday_runtime = time(hour=14, minute=0, tzinfo=utc)
history_runtime = time(hour=16, minute=0, tzinfo=utc)

def get_holiday():
    ## Select a random holiday from holidays.json for today's date
    holidays_df = pd.read_json('holidays.json')
    today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
    holidays_df = holidays_df.loc[holidays_df['Date'] == today]
    holiday_row = holidays_df.sample()
    holiday_name = holiday_row['Holiday'].item()
    holiday_link = holiday_row['Link'].item()

    return holiday_name, holiday_link

def get_history():
    ## Select a random historical event from hisotry.json for today's date
    history_df = pd.read_json('history.json')
    today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
    history_df = history_df.loc[history_df['Date'] == today]
    history_row = history_df.sample()
    history_year = history_row['Year'].item()
    history_event = history_row['Event'].item()
    history_description = history_row['Description'].item()

    return str(history_year), history_event, history_description

def get_random_member(server_input):
    ## Select a member of the server at random and make sure member is not a bot
    member = random.choice(server_input.guild.members)
    while member.bot == True:
        member = random.choice(server_input.guild.members)
    return member

def get_holiday_messages(holiday_name: str, holiday_link, member):
    ## Create messages/embeds that the bot will send out
    response1 = f'🎉🎉🎉 Time to celebrate! Today is {holiday_name}! 🎉🎉🎉'
    embed = discord.Embed(title=holiday_name,
                          url=holiday_link
                        )
    embed.url = holiday_link
    response2 = f'{member.mention} let everyone know how you\'re celebrating {holiday_name}!'
    return response1, embed, response2

def get_history_messages(history_year: str, history_event: str, history_description: str):
    ## Create messages/embeds that the bot will send out
    response1 = f'🎉🥂🎆 Let\'s celebrate history! On this day in {history_year}, {history_event} 🎆🥂🎉'
    response2 = f'{history_description}'
    return response1, response2

## Run CelebrationBot message with !celebrate command
@bot.command(name='celebrate')
async def my_command(ctx):
    
    holiday_name, holiday_link = get_holiday()
    member = get_random_member(ctx)
    response1, embed, response2 = get_holiday_messages(holiday_name,holiday_link,member)

    await ctx.send(response1)
    await ctx.send(embed=embed)
    await ctx.send(response2)

## Run CelebrationBot historical event message with !history command
@bot.command(name='history')
async def my_command(ctx):
    
    history_year, history_event, history_description = get_history()
    response1, response2 = get_history_messages(history_year, history_event, history_description)

    await ctx.send(response1)
    await ctx.send(response2)

## Run CelebrationBot celebration message at 10:00AM Eastern time every day
@tasks.loop(time=holiday_runtime)
async def holidays_task():
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
    
    response1, embed, response2 = get_holiday_messages(holiday_name,holiday_link,member)
    await channel.send(response1)
    await channel.send(embed=embed)
    await channel.send(response2)

## Run CelebrationBot history message at 12:00PM Eastern time every day
@tasks.loop(time=history_runtime)
async def history_task():
    history_year, history_event, history_description = get_history()
    ## Get the channel that the bot messages will be sent to
    ## Defaults to first channel in the server
    text_channel_list = []
    for server in bot.guilds:
        for channel in server.channels:
            if str(channel.type) == 'text':
                text_channel_list.append(channel)
    channel = text_channel_list.pop(0)
    
    response1, response2 = get_history_messages(history_year, history_event, history_description)
    await channel.send(response1)
    await channel.send(response2)

## On bot startup initialize the timed tasks
@bot.event
async def on_ready(): 
    ## Start the holiday and history task loop runs first
    holidays_task.start()
    history_task.start()
bot.run(TOKEN)