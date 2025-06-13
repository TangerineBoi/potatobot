#thank you for all the apis. made by potato boi

#table of contents
#game api
#anime api
#game bot
#join vc

# This example requires the 'message_content' intent.
from discord.ext import commands, tasks
import nest_asyncio
import discord
import time

#api
import requests
import aiohttp  # Use aiohttp for asynchronous requests
from jikanpy import Jikan
import asyncio
from jikan4snek import Jikan4SNEK
jikan = Jikan()
jikan = Jikan4SNEK(debug=True)

#game
import random
import json
import os

#start
bot = commands.Bot(command_prefix ='!', intents = discord.Intents.all())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "potato" in message.content.lower():
        await message.channel.send('potato!!!')
    
    

    await bot.process_commands(message)

@bot.command(brief='Test.', description='Test if the bot works, with ping-pong message.')
async def test(ctx):

    start_time = time.time()

    await ctx.send("working!")

    end_time = time.time()
    duration = end_time - start_time

    await ctx.send(f'Message relay time: {duration:.3f} seconds')  # testing command


@bot.command(brief='Shows you the lowest price recorded for a game.')
async def deals(ctx, title: str, numSearch: int):

    url = f"https://www.cheapshark.com/api/1.0/games?title={title}"
    
    # Make an API request
    response = requests.get(url)
    # Use aiohttp for asynchronous request
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()  # Parse the JSON response
                await ctx.send('Lowest price for these games: ')

                for i in range(numSearch):
                    title = data[i]['external']
                    price = data[i]['cheapest']
                    gameID = data[i]['steamAppID']
                    await ctx.send(f'Game: [{title}](<https://store.steampowered.com/app/{gameID}>) at ${price}.')
                    i += 1
            else:
                await ctx.send("error, please try again later")



@bot.command(brief='Search some anime using (prefix)anime (name)')
async def anime(ctx, *, search: str):

    url = f"https://api.jikan.moe/v4/anime?q={search}"
    

    # Make an API request
    response = requests.get(url)
    # Use aiohttp for asynchronous request
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    data = await response.json()  # Parse the JSON response
                    
                    animeName = str(data['data'][0]["url"])
                    
                    title = str(data['data'][0]['titles'][0]['title'])   #WTF??? LOL
                    await ctx.send(f"Anime name: {title} \n{animeName}")
                except:
                    await ctx.send("Anime not found.")
        

#GAME SETUP (JSON FILE)
   # Create a simple database file (JSON format) to store user data
if not os.path.exists('economy.json'):
    with open('economy.json', 'w') as f:
        json.dump({}, f)

    # Load the economy data from file
def load_data():
    with open('economy.json', 'r') as f:
        return json.load(f)

# Save the economy data to file
def save_data(data):
    with open('economy.json', 'w') as f:
        json.dump(data, f, indent=5)

# STATS
@bot.command(brief='Shows all stats.')
async def s(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    balance = int(data[user_id]["balance"])
    energy = data[user_id]["energy"]
    if user_id not in data:
        data[user_id] = {'balance': 100, 'energy': 100, 'mult':1, 'base':1, 'inv': []}  # Give a starting balance if the user doesn't have one
        save_data(data) 
        await ctx.send(f"Hello new player! Your balance is ${balance}.\n You have {energy} energy.")    
    else:
        await ctx.send(f"You have ${int(balance)}.\nYou have {int(energy)} energy.\nYou have a {data[user_id]['mult']:.1f}x job multiplier.\nBase work stats: {data[user_id]['base']}")


#  RESET      
@bot.command(brief='Resets all values.')
async def reset(ctx):
    data = load_data()  
    user_id = str(ctx.author.id)
    data[user_id] = {'balance': 100, 'energy': 100, 'base': 1,'mult':1, 'inv': []}  # hard reset
    save_data(data)
    balance = data[user_id]['balance']
    await ctx.send(f'Reset complete.\n Balance: ${balance}. \nEnergy:{data[user_id]["energy"]}.\nBase: {data[user_id]["base"]}\nMult:{data[user_id]["mult"]}') 

#    WORK
@bot.command(brief='Work to gain money.', description='Gain money, lose energy.')  
async def w(ctx, place: str):
    data = load_data()  
    user_id = str(ctx.author.id)
    
    if place == "o":

        try:
            randWork = random.randint(1 + data[user_id]['base'],6 + data[user_id]['base'])  #rand num
            data[user_id]['energy'] -= 10 
            randWorkNum1 = random.randint(10,50)
            randWorkNum2 = random.randint(20,50)
            
            if data[user_id]['energy'] > 0:
                await ctx.send(f'What is {randWorkNum1} + {randWorkNum2}?')
                def check(m):
                    #Check if the user's answer is correct.
                    return m.author == ctx.author and m.channel == ctx.channel


                # Wait for the user to respond to the question
                response = await bot.wait_for('message', check=check, timeout=10.0)

                if int(response.content) == (randWorkNum1 + randWorkNum2):
                    data[user_id]['balance'] += randWork * data[user_id]['mult'] #get money    
                    await ctx.send(f"Correct, work complete. You earned ${int(randWork)} * {data[user_id]['mult']:.1f}x. \nYour balance is now ${int(data[user_id]['balance'])  }. \nYou have {data[user_id]['energy']} energy.")
                    save_data(data)
                else:   #fail
                    data[user_id]['balance'] -= randWork
                    await ctx.send(f"Work failed! You lost ${int(randWork)}.\nNew balance: ${data[user_id]['balance']}.")
                    save_data(data)
                if data[user_id]["balance"] < 0:
                    await ctx.send("\nYou failed and died on the streets. GG\nYour stats were reset, hopefully in this life you prosper.")
                    data[user_id] = {'balance': 100, 'energy': 100, 'mult':1, 'base': 1}
                    save_data(data)
            else:
                await ctx.send('You are depressed and cannot work!')
        except:
            await ctx.send('error occured!')  #error

    elif place == "c":
        data = load_data()  
        user_id = str(ctx.author.id)
        await ctx.send('You look for hidden treasures and loot.')
        randGold = random.randint(1,20)
        randLoot = random.randint(1,10)
        randTrash = random.randint(1,5)

        if randGold == 5:
            await ctx.send('Found gold!!!')
            data[user_id][inv].append("gold")
        if randLoot == 5:
            await ctx.send('Found loot!')
            data[user_id][inv].append("loot")
        if randTrash == 2:
            await ctx.send('Found trash...')
            data[user_id][inv].append("trash")
        if randGold != 5 and randLoot != 5 and randTrash != 2:
            await ctx.send('You went home emptyhanded :(') 


##  SHOP
def pillsCost(ctx):
    data = load_data()  
    user_id = str(ctx.author.id)
    return int(((data[user_id]['balance'])) * 0.5) + 10

def workCost(ctx):
    data = load_data()  
    user_id = str(ctx.author.id)
    return int(pillsCost(ctx) + (10 * data[user_id]['mult']))
    
@bot.command(brief='Shop.', description='Lose money, gain energy(and upgrades(?))')  
async def shop(ctx):
    global snackPrice 
    global mealPrice
    snackPrice = 10     
    mealPrice = 30
    data = load_data()  
    user_id = str(ctx.author.id)
    await ctx.send(f'Get your energy fix. Use !buy (item). \n:chocolate_bar: SNACK (+30 energy, -0.1x MULT) --- ${snackPrice}\n:stew: MEAL (+50 energy) --- ${mealPrice}\n:person_lifting_weights: WORKOUT (+1 BASE) --- ${workCost(ctx)}\n:pill: PILLS(+0.5x MULT) --- ${int(pillsCost(ctx))}')

## BUY
@bot.command(brief='Buy things from shop.', description='Go buy stuff.')
async def buy(ctx, item: str):
    global snackPrice 
    global mealPrice
    snackPrice = 10     ###PRICES!!
    mealPrice = 30
    data = load_data()  
    user_id = str(ctx.author.id)

    if item.lower() == 'snack':
        if data[user_id]['balance'] >= snackPrice:
            data[user_id]['energy'] += 30
            data[user_id]['mult'] -= 0.1
            data[user_id]['balance'] -= snackPrice
            await ctx.send('Yum. +30 energy, -0.1x MULT')
        else:
            await ctx.send("Not enough money.")
    elif item.lower() == 'meal':
        if data[user_id]['balance'] >= mealPrice:
            data[user_id]['energy'] += 50
            data[user_id]['balance'] -= mealPrice
            await ctx.send('Heck yeah!! +50 energy')
        else:
            await ctx.send("Not enough money.")
    elif item.lower() == 'workout':
        if data[user_id]['balance'] >= workCost(ctx):
            data[user_id]['base'] += 1
            data[user_id]['balance'] -= workCost(ctx)
            await ctx.send('That was tiring but you feel a bit stronger. +1 BASE.')    
        else:
            await ctx.send("Not enough money.")   
    elif item.lower() == 'pills':
        if data[user_id]['balance'] >= pillsCost(ctx):
            data[user_id]['mult'] += 0.5
            data[user_id]['balance'] -= pillsCost(ctx)
            await ctx.send('You feel energized. +0.5x MULT')
        else:
            await ctx.send("Not enough money.")
    else:
        await ctx.send("That's not an item.")

    
    save_data(data)

@bot.command(brief='They might be worth something.', description='read desc.')
async def inv(ctx):
    data = load_data()  
    user_id = str(ctx.author.id)
    await ctx.send(f'{data[user_id][inv]}')

@bot.command(brief='Make the bot join a voice channel',description='join vc')
async def join(ctx):
    member = ctx.author
    channel = ctx.message.author.voice.channel
    if member.voice and member.voice.channel:
        await ctx.send(f"Joining {channel.name}")
        await channel.connect()
    else:
        await ctx.send("You are not in a vc")



####TOKEN! KEEP SAFE!
bot.run(botToken)

##ideas#
#energy meter?
#shop?
#getting bot onto vc?  ####DONE!
#implementing char.ai? (CANT DO CHAR.AI!! OPENAI MAYBE)   
#bot using TTS from the AI?
#being able to use speech to text to talk to the AI?

## errors: 
#inv command
#actually getting loot in inv
