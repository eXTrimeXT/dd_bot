import discord

from conf import *
from Music import *
from MyBot import MyBot

@bot.event
async def on_ready():
    await bot.add_cog(Music(bot))
    await bot.add_cog(MyBot(bot))
    logger("MAIN", f"{bot.user.name} is ONLINE")
    await bot.change_presence(activity=discord.CustomActivity(name=f'Текущий хост - {CURRENT_HOST}'))


@bot.event
async def on_member_join(member):
    await discord.channel.send(embed=discord.Embed(
        description=f"Новый пользователь: ``{member.name}``",
        colour=discord.Colour.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255))))



logger("MAIN", "SERVER OFF")
TOKEN = sys.argv[1]
bot.run(TOKEN)