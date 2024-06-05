from conf import *


class MyBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger("MyCommands", "__init__")

    @commands.command(name="botstop", aliases=["ботстоп"])
    async def _botstop(self, ctx: commands.Context):
        if ctx.message.author.id == 552140044379357184:
            await ctx.send("Владелец отключил бота!")
            await self.bot.close()

    @commands.command(name="clear", aliases=["очистить"])
    @commands.has_permissions(administrator=True)
    async def _clear(self, ctx: commands.Context, amount=50):
        try:
            logger("MyCommands: clear", f"Удаляется {amount} сообщений!")
            await ctx.channel.purge(limit=amount+1)
            logger("MyCommands: clear", f"Удалено сообщений: {amount}")
            emb = discord.Embed(description=f"✅Удалено сообщений: {amount}", colour=discord.Colour.from_rgb(0, 255, 0))
        except:
            emb = discord.Embed(description=f"❎Не удалось обработать так много сообщений, попробуйте меньшее количество!", colour=discord.Colour.from_rgb(255, 0, 0))
        finally:
            await ctx.send(embed=emb)

    # Позволяет писать от имени бота
    @commands.command(name = "wab", aliases = ["отбота"])
    @commands.has_permissions(administrator=True)
    async def _writeasbot(self, ctx: commands.Context, *, text):
        await ctx.channel.purge(limit=1)
        await ctx.send(text)
        logger("MyCommands: writeasbot", f"{ctx.author}: {text}")

    @commands.command(name="version", aliases=["версия"])
    async def _version(self, ctx: commands.Context):
        await ctx.send(f"{ctx.message.author.mention}, Версия бота: {VERSION}")

    @commands.command(name="ping", aliases = ["пинг"])
    async def _ping(self, ctx: commands.Context):
        ping = round(self.bot.latency * 1000)
        emb = discord.Embed(description=f":green_circle:``{ping}мс``", colour=discord.Colour.from_rgb(0, 0, 255))
        await ctx.send(embed=emb)

    @commands.command(name="update", aliases=["обновление"])
    async def _update(self, ctx: commands.Context):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title=f"`ОБНОВЛЕНИЕ! Я обновился до версии {VERSION}`", description=f"{TEXT_UPDATE}", colour=discord.Colour.from_rgb(0, 255, 0))
        await ctx.send(embed=emb)

    @commands.command(name="ava", aliases=["ава"])
    async def _avatar(self, ctx: commands.Context, *, member:discord.Member = None):
        if not member:
            member = ctx.message.author
        emb = discord.Embed(title=str(member), colour=0x00ff00)
        emb.set_image(url=member.avatar)
        await ctx.reply(embed=emb, mention_author=False)

    async def get_embed(self, ctx, title, embed):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(
            title=title,
            colour=discord.Colour.from_rgb(255, 0, 0),
            description=embed,
        )
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        emb.set_footer(text=ctx.author.name, icon_url=ctx.message.author.avatar)
        await ctx.send(embed=emb)

    @commands.command(name="alias", aliases=["псевдонимы"])
    async def _aliases(self, ctx: commands.Context):
        await self.get_embed(ctx, title="`ПСЕВДОНИМЫ: `", embed=EMB_ALIASES)

    @commands.command(name="help", aliases=["помощь"])
    async def _help(self, ctx: commands.Context):
        await self.get_embed(ctx, title="HELP: ``Не забывайте про префикс '!'``", embed=EMB_HELP)

    # @commands.command(name="help_gpt", aliases=["помощь_ии"])
    # async def _help_gpt(self, ctx: commands.Context):
    #     await self.get_embed(ctx, title="HELP: ``Не забывайте про префикс '!'``", embed=EMB_GPT)

    # @commands.command(name="rainbow", aliases=["радуга"])
    # async def _rainbow(self, ctx: commands.Context, variant="rnd", time=5.0):
    #     if 60.0 < time or time < 1.0:
    #         embed = discord.Embed(description=f"{ctx.author.mention}, границы скорости от 1 до 60 секунд, ты ввел {time}!", color=0x000000)
    #         time = 5
    #         await ctx.send(embed=embed)
    #
    #     role = discord.utils.get(ctx.guild.roles, id=1139160276479004794)  # id-роли 1139160276479004794
    #     await ctx.author.add_roles(role)
    #
    #     if variant == "off":
    #         for member in ctx.guild.members:
    #             await member.remove_roles(role)
    #             embed = discord.Embed(description=f"Радуга у всех выключена!", color=0x000000)
    #         await ctx.send(embed=embed)
    #
    #     elif variant == "all":
    #         for member in ctx.guild.members:
    #             await member.add_roles(role)
    #             embed = discord.Embed(description=f"Радуга у всех включена!", color=0x000000)
    #         await ctx.send(embed=embed)
    #
    #     elif variant == "on":
    #         colours = [0xff0000, 0xff9f00, 0x72ff00, 0x00ff6d, 0x00acff, 0x0200ff, 0xc500ff, 0xff0053, 0xFA8072,
    #                    0xFF7F50, 0x00CED1, 0x800080, 0x696969]  # цвет в формате 0xHEX
    #         embed = discord.Embed(description=f"Радуга у {ctx.author.mention} включена!\nСкорость = {time} сек!",
    #                               color=0x000000)
    #         await ctx.send(embed=embed)
    #
    #         while variant == "on":
    #             await role.edit(colour=choice(colours))
    #             await asyncio.sleep(time)
    #
    #     elif variant == "rnd":
    #         embed = discord.Embed(description=f"Радуга у {ctx.author.mention} включена!\nСкорость = {time} сек!",
    #                               color=0x000000)
    #         await ctx.send(embed=embed)
    #
    #         while variant == "rnd":
    #             await role.edit(colour=discord.Color(randint(0x000000, 0xFFFFFF)))
    #             await asyncio.sleep(time)
