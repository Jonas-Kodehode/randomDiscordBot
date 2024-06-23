from discord.ext import commands # type: ignore

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def greet(self, ctx):
        await ctx.send('Hello from a cog!')

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))