from moderation import *
from my_bot import *
from music import *
from apps import *

@bot.event
async def on_ready():
    await bot.add_cog(MyCommands(bot))
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(Music(bot))
    await bot.add_cog(Apps(bot))
    logger("MAIN", f"{bot.user.name} is ONLINE")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(ID_MAIN_CHANNEL)
    role = discord.utils.get(member.guild.roles, id=ID_FIRST_ROLE)
    await member.add_roles(role)
    logger("on_member_join", f"Новый юзер - {member.name}")
    await channel.send(embed=discord.Embed(
        description=f"Новый пользователь: ``{member.name}``",
        colour=discord.Colour.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255))))


logger("MAIN", "SERVER OFF")
bot.run(TOKEN)