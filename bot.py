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

# Commands
@bot.command(name='commands', help='Lists all available commands')
async def list_commands(ctx):
    commands_list = []
    for command in bot.commands:
        # Skipping commands without a brief or help attribute will hide them from the list
        if command.help:
            commands_list.append(f'**{command.name}**: {command.help}')
    
    commands_message = '\n'.join(commands_list)
    await ctx.send(commands_message)


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


@bot.command( name='ping', help='Responds with "Pong!"')
async def ping(ctx):
    await ctx.send('Pong!')


@bot.command(name="meme", help="Displays a random programmer meme")
async def meme(ctx):
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
                await ctx.send("Failed to fetch meme image due to unexpected data format.")

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


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel_id = 1254429580656115727  
    channel = bot.get_channel(channel_id)
    msg = random.choice(messages)
    if channel: 
        await channel.send(msg)




# Run the bot
if TOKEN:
    bot.run(TOKEN)
    print("Bot is running.")
else:
    print("Token not found. Please set the DISCORD_BOT_TOKEN environment variable.")