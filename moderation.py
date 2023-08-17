from conf import *

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger("Moderation", "__init__")


    @commands.command(name = "status", aliases = ["статус"])
    @commands.has_permissions(administrator=True)
    async def _setstatus(self, ctx: commands.Context, *, status : str):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f"{status}"))
        await ctx.send(f"{ctx.message.author.mention}, статус изменён на {status}")


    @commands.command(name="clear", aliases = ["cls"])
    @commands.has_permissions(administrator=True)
    async def _clear(self, ctx: commands.Context, amount=100):
        logger("MyCommands: clear", f"Удаляется {amount} сообщений!")
        await ctx.channel.purge(limit=amount+1)
        logger("MyCommands: clear", f"Удалено сообщений: {amount}")
        emb = discord.Embed(description=f"✅Удалено сообщений: {amount}", colour=discord.Colour.from_rgb(0, 255, 0))
        await ctx.send(embed=emb)


    # Позволяет писать от имени бота
    @commands.command(name = "wab", aliases = ["отбота"])
    @commands.has_permissions(administrator=True)
    async def _writeasbot(self, ctx: commands.Context, *, text):
        await ctx.channel.purge(limit=1)
        await ctx.send(f"``{text}``")
        logger("MyCommands: writeasbot", f"{ctx.author}: {text}")


    @commands.command(name="kick", aliases=["кик"])
    @commands.has_permissions(administrator=True)
    async def _kick(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        await ctx.channel.purge(limit=1)

        if reason is None:
            emb = discord.Embed(
                description=f"✅Кик участника {member.name}",
                colour=discord.Colour.from_rgb(255, 0, 0)
            )
            await member.kick()
        else:
            emb = discord.Embed(
                description=f"✅Кик участника {member.name}\nПричина:{reason}",
                colour=discord.Colour.from_rgb(255, 0, 0)
            )
            await member.kick(reason=reason)

        await ctx.send(embed=emb)


    @commands.command(name="ban", aliases=["бан"])
    @commands.has_permissions(administrator=True)
    async def _ban(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        await ctx.channel.purge(limit=1)

        if reason is None:
            emb = discord.Embed(
                description=f"✅Бан участника: {member.name}",
                colour=discord.Colour.from_rgb(255, 0, 0)
            )
            await member.ban()
        else:
            emb = discord.Embed(
                description=f"✅Бан участника {member.name}\nПричина:{reason}",
                colour=discord.Colour.from_rgb(255, 0, 0)
            )
            await member.ban(reason=reason)

        await ctx.send(embed=emb)


    @commands.command(name="botstop", aliases=["ботстоп"])
    @commands.is_owner()
    async def botstop(self, ctx: commands.Context):
        logger("botstop", "До свидания")
        emb = discord.Embed(
            description="Я пошел обновляться, скоро вернусь обратно",
            colour=discord.Colour.from_rgb(255,255,0)
        )
        await ctx.send(embed=emb)
        await bot.logout()