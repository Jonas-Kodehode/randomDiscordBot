from dotenv import load_dotenv
load_dotenv()

import prints
import random
import discord 
from discord.ext import commands 
import os
import aiohttp
import logging
import html
import asyncio
from bs4 import BeautifulSoup

# Messages
messages = prints.messages

# Define intents
intents = discord.Intents.default()  # This enables the default intents
intents.messages = True  # If your bot needs to listen to messages
intents.guilds = True # If your bot needs to interact with guild information
intents.message_content = True

# Command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Defining api keys
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CAT_API_KEY = os.getenv("CAT_API_KEY")
MEME_API_KEY = os.getenv("MEME_API_KEY")
GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel_id = 1254429580656115727
    channel = bot.get_channel(channel_id)
    msg = random.choice(messages)
    if channel:
        await channel.send(msg)


# Commands
# Listing all available commands
@bot.command(name='commands', help='Lists all available commands')
async def list_commands(ctx):
    commands_list = []
    for command in bot.commands:
        # Skipping commands without a brief or help attribute will hide them from the list
        if command.help:
            commands_list.append(f'**{command.name}**: {command.help}')
    
    commands_message = '\n'.join(commands_list)
    await ctx.send(commands_message)

# Cat images
@bot.command(name='cat', help='Displays a random cat image')
async def cat(ctx):
    api_url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": CAT_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                cat_image_url = data[0]['url']
                await ctx.send(cat_image_url)
            else:
                await ctx.send("Failed to fetch cat image.")


# Ping pong test
@bot.command( name='ping', help='Responds with "Pong!"')
async def ping(ctx):
    await ctx.send('Pong!')


# Programming memes
@bot.command(name="programmingMeme", help="Displays a random programming meme")
async def progMeme(ctx):
    url = "https://programming-memes-images.p.rapidapi.com/v1/memes"
    headers = {
        "x-rapidapi-key": MEME_API_KEY,
        "x-rapidapi-host": "programming-memes-images.p.rapidapi.com"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
            try:
                meme_image_url = data[0]['image']
                await ctx.send(meme_image_url)
            except (KeyError, IndexError) as e:
                await ctx.send("Beep, boop!")


#Reddit memes 
@bot.command(name="meme", help="Displays a random meme")
async def meme(ctx):
    url = "https://reddit-meme.p.rapidapi.com/memes/trending"
    headers = {
        "x-rapidapi-key": MEME_API_KEY,
        "x-rapidapi-host": "reddit-meme.p.rapidapi.com"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
            try:
                meme_image_url = data[0]['image']
                await ctx.send(meme_image_url)
            except (KeyError, IndexError) as e:
                await ctx.send("Beep, boop!, " + str(e))


# Quiz
@bot.command(name='trivia', help='Starts a trivia game with a random question')
async def trivia(ctx):
    url = 'https://opentdb.com/api.php?amount=1&type=multiple'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                question = data['results'][0]
                question_text = html.unescape(question['question'])
                correct_answer = html.unescape(question['correct_answer'])
                incorrect_answers = [html.unescape(answer) for answer in question['incorrect_answers']]
                all_answers = incorrect_answers + [correct_answer]
                random.shuffle(all_answers)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                options_text = "\n".join([f"{i+1}. {answer}" for i, answer in enumerate(all_answers)])
                await ctx.send(f"**Trivia Question:**\n{question_text}\n\n**Options:**\n{options_text}")

                try:
                    user_response = await bot.wait_for('message', check=check, timeout=30)
                    answer_index = int(user_response.content.strip()) - 1
                    if all_answers[answer_index] == correct_answer:
                        await ctx.send(f"Correct! 🎉 The answer was: {correct_answer}")
                    else:
                        await ctx.send(f"Oops! The correct answer was: {correct_answer}")
                except Exception as e:
                    await ctx.send(f"Time's up! The correct answer was: {correct_answer}")


# Movie search
@bot.command(name='movie', help='Fetches information about a movie from OMDB')
async def movie(ctx, *, movie_name: str):
    MOVIE_API_KEY = os.getenv("MOVIE_API_KEY")
    url = f'http://www.omdbapi.com/?apikey={MOVIE_API_KEY}&t={movie_name}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['Response'] == 'True':
                    embed = discord.Embed(title=data['Title'], description=data['Plot'], color=0x00ff00)
                    embed.set_thumbnail(url=data['Poster'])
                    embed.add_field(name='Year', value=data['Year'], inline=True)
                    embed.add_field(name='Released', value=data['Released'], inline=True)
                    embed.add_field(name='Runtime', value=data['Runtime'], inline=True)
                    embed.add_field(name='Genre', value=data['Genre'], inline=True)
                    embed.add_field(name='Director', value=data['Director'], inline=True)
                    embed.add_field(name='Actors', value=data['Actors'], inline=True)
                    embed.add_field(name='IMDB Rating', value=data['imdbRating'], inline=True)
                    embed.add_field(name='Box Office', value=data['BoxOffice'], inline=True)
                    
                    ratings = data.get('Ratings', [])
                    for rating in ratings:
                        embed.add_field(name=rating['Source'], value=rating['Value'], inline=True)
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Movie not found: {movie_name}")
            else:
                await ctx.send("Failed to fetch movie information.")


# Coin Flipper
@bot.command(name='flip', help='Flips a coin and returns either Heads or Tails')
async def flip(ctx):
    flipping_messages = [
        "Flipping the coin... 🪙",
        "Flipping the coin... 🪙 Heads...",
        "Flipping the coin... 🪙 Tails...",
        "Flipping the coin... 🪙 Heads...",
        "Flipping the coin... 🪙 Tails...",
        "Flipping the coin... 🪙 Heads...",
        "Flipping the coin... 🪙 Tails...",
    ]
    message = await ctx.send(flipping_messages[0])
    
    for i in range(1, len(flipping_messages)):
        await asyncio.sleep(0.2)  # Add a 0.5 second delay between messages
        await message.edit(content=flipping_messages[i])
    
    await asyncio.sleep(0.5)
    result = random.choice(['Heads', 'Tails'])
    await message.edit(content=f'The coin landed on: {result} 🎉')

# Dice Roller
@bot.command(name='roll', help='Rolls a die. Optionally specify 6 or 20 for the number of sides (e.g., !roll 20 for a 20-sided die).')
async def roll(ctx, sides: int = 6):
    if sides not in [6, 20]:
        await ctx.send("Please specify either 6 or 20 sides for the die.")
        return
    
    rolling_messages = {
        6: [
            "Rolling the 6-sided die... 🎲",
            "Rolling the 6-sided die... 🎲 1...",
            "Rolling the 6-sided die... 🎲 2...",
            "Rolling the 6-sided die... 🎲 3...",
            "Rolling the 6-sided die... 🎲 4...",
            "Rolling the 6-sided die... 🎲 5...",
            "Rolling the 6-sided die... 🎲 6..."
        ],
        20: [
            "Rolling the 20-sided die... 🎲",
            "Rolling the 20-sided die... 🎲 1...",
            "Rolling the 20-sided die... 🎲 2...",
            "Rolling the 20-sided die... 🎲 3...",
            "Rolling the 20-sided die... 🎲 4...",
            "Rolling the 20-sided die... 🎲 5...",
            "Rolling the 20-sided die... 🎲 6...",
            "Rolling the 20-sided die... 🎲 7...",
            "Rolling the 20-sided die... 🎲 8...",
            "Rolling the 20-sided die... 🎲 9...",
            "Rolling the 20-sided die... 🎲 10...",
            "Rolling the 20-sided die... 🎲 11...",
            "Rolling the 20-sided die... 🎲 12...",
            "Rolling the 20-sided die... 🎲 13...",
            "Rolling the 20-sided die... 🎲 14...",
            "Rolling the 20-sided die... 🎲 15...",
            "Rolling the 20-sided die... 🎲 16...",
            "Rolling the 20-sided die... 🎲 17...",
            "Rolling the 20-sided die... 🎲 18...",
            "Rolling the 20-sided die... 🎲 19...",
            "Rolling the 20-sided die... 🎲 20..."
        ]
    }
    
    message = await ctx.send(rolling_messages[sides][0])
    
    for i in range(1, min(len(rolling_messages[sides]), 7)):
        await asyncio.sleep(0.2)  # Add a 0.5 second delay between messages
        await message.edit(content=rolling_messages[sides][i])
    
    await asyncio.sleep(0.5)
    result = random.randint(1, sides)
    await message.edit(content=f'The die landed on: {result} 🎉')


# Lyrics
@bot.command(name='lyrics', help='Fetches the lyrics for a specified song')
async def lyrics(ctx, *, song_title: str):
    url = f'https://api.genius.com/search?q={song_title}'
    headers = {
        'Authorization': f'Bearer {GENIUS_API_KEY}'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data['response']['hits']:
                    song_info = data['response']['hits'][0]['result']
                    song_url = song_info['url']

                    async with session.get(song_url) as song_response:
                        if song_response.status == 200:
                            soup = BeautifulSoup(await song_response.text(), 'html.parser')
                            lyrics = ''

                            for div in soup.find_all("div", class_=lambda x: x and x.startswith("Lyrics__Container")):
                                for br in div.find_all("br"):
                                    br.replace_with("\n")
                                lyrics += div.get_text(separator='\n').strip() + "\n"

                            if lyrics.strip():
                                # Create and send embeds
                                title = song_info['full_title']
                                thumbnail = song_info['song_art_image_thumbnail_url']
                                url = song_info['url']
                                
                                # Split lyrics into chunks of up to 2000 characters
                                chunks = [lyrics[i:i+1024] for i in range(0, len(lyrics), 1024)]
                                for i, chunk in enumerate(chunks):
                                    embed = discord.Embed(title=title if i == 0 else '', description=chunk, color=0x1DB954, url=url)
                                    if i == 0:
                                        embed.set_thumbnail(url=thumbnail)
                                    await ctx.send(embed=embed)
                            else:
                                await ctx.send('Lyrics not found.')
                        else:
                            await ctx.send("Failed to fetch lyrics from Genius.")
                else:
                    await ctx.send(f"No lyrics found for {song_title}")
            else:
                await ctx.send("Failed to fetch lyrics.")




# Events
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide all required arguments.')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found.')
    else:
        # Log the error type and message for debugging
        logging.error(f'Unhandled error: {type(error).__name__}: {error}')
        await ctx.send('An error occurred.')



# Run the bot
if TOKEN:
    bot.run(TOKEN)
    print("Bot is running.")
else:
    print("Token not found. Please set the DISCORD_BOT_TOKEN environment variable.")