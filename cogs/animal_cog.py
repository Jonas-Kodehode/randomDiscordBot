from dotenv import load_dotenv # type: ignore
load_dotenv()

from discord.ext import commands
import aiohttp
import os

API_KEY = os.getenv("CAT_API_KEY")

class Animals(commands.Cog, name="Animals"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cat', help='Displays a random cat image')
    async def cat(self, ctx):
        api_url = "https://api.thecatapi.com/v1/images/search"
        headers = {"x-api-key": API_KEY}
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    cat_image_url = data[0]['url']
                    await ctx.send(cat_image_url)
                else:
                    await ctx.send("Failed to fetch cat image.")

# Function to setup the cog
async def setup(bot):
    bot.add_cog(Animals(bot))