from conf import *


class MyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger("MyCommands", "__init__")


    @commands.command(name = "grant", aliases = ["подарок"])
    async def _grant(self, ctx: commands.Context):
        await ctx.send(f"{bot.user.name}: ")



    @commands.command(name = "knb", aliases = ["кнб"])
    async def _knb(self, ctx: commands.Context, user_element: str):
        bot_element = {2: "бумага", 1: "камень", 0: "ножницы"}
        id_element = randint(0, 2)

        if user_element == "бумага" or user_element == "камень" or user_element == "ножницы" or user_element == "fuck":
            if bot_element[id_element] == user_element:
                await ctx.send(f"{bot.user.name}: {bot_element[id_element]} | {ctx.message.author.mention}: {user_element}\nНичья!")

            elif user_element == "fuck":
                await ctx.send(f"{ctx.message.author.mention} победитель!")

            elif bot_element[id_element] == "бумага" and user_element == "ножницы":
                await ctx.send(f"{bot.user.name}: {bot_element[id_element]} | {ctx.message.author.mention}: {user_element}\n{ctx.message.author.mention} победитель!")
            
            elif bot_element[id_element] == "ножницы" and user_element == "бумага":
                await ctx.send(f"{bot.user.name}: {bot_element[id_element]} | {ctx.message.author.mention}: {user_element}\n{bot.user.name} победитель!")

            elif bot_element[id_element] > user_element:
                await ctx.send(f"{bot.user.name}: {bot_element[id_element]} | {ctx.message.author.mention}: {user_element}\n{ctx.message.author.mention} победитель!")
            
            elif bot_element[id_element] < user_element:
                await ctx.send(f"{bot.user.name}: {bot_element[id_element]} | {ctx.message.author.mention}: {user_element}\n{bot.user.name} победитель!")
        else:
            await ctx.send(f"{ctx.message.author.mention}, выбирите камень/ножницы/бумага, а не `{user_element}`")


    @commands.command(name="version", aliases = ["v"])
    async def _version(self, ctx: commands.Context):
        await ctx.send(f"{ctx.message.author.mention}, Версия бота: {VERSION}")


    @commands.command(name = "ping", aliases = ["пинг"])
    async def _ping(self, ctx: commands.Context):
        ping =  round(self.bot.latency * 1000)
        emb = discord.Embed(description=f":green_circle:``{ping}мс``", colour=discord.Colour.from_rgb(0, 0, 255))
        await ctx.send(embed=emb)


    @commands.command(name = "vk", aliases=["вк"])
    async def _vk(self, ctx: commands.Context):
        author = ctx.message.author.mention
        emb = discord.Embed(
            title="VK", url="https://vk.com/red_line_linux",
            description="Оцени мою группу по программированию!",
            colour=discord.Colour.from_rgb(0, 255, 0))
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        emb.set_image(url="https://sun9-85.userapi.com/impg/pgD4sKUOe83D_8k9Ih8x3tphuV6PgF1zbVXtUA/Ux63dI7VZnY.jpg?size=1920x1080&quality=96&sign=4c602accf5be6be4712e31f4becff431&type=album")
        emb.set_thumbnail(url="https://sun9-85.userapi.com/impg/pgD4sKUOe83D_8k9Ih8x3tphuV6PgF1zbVXtUA/Ux63dI7VZnY.jpg?size=1920x1080&quality=96&sign=4c602accf5be6be4712e31f4becff431&type=album")
        await ctx.send(embed=emb)


    @commands.command(name = "update", aliases=["обновление", "u"])
    async def _update(self, ctx: commands.Context):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title=f"`ОБНОВЛЕНИЕ! Я обновился до версии {VERSION}`", description=f"{TEXT_UPDATE}", colour=discord.Colour.from_rgb(0, 255, 0))
        await ctx.send(embed=emb)


    @commands.command(name = "ava", aliases = ["ава"])
    async def _avatar(self, ctx: commands.Context, *, member:discord.Member = None):
        if not member:
            member = ctx.message.author
        emb = discord.Embed(title=str(member), colour=0x00ff00)
        emb.set_image(url=member.avatar_url)
        await ctx.reply(embed=emb, mention_author=False)


    @commands.command(name = "alias", aliases = ["псевдонимы"])
    async def _aliases(self, ctx: commands.Context):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(
            title = "`ПСЕВДОНИМЫ: `",
            colour=discord.Colour.from_rgb(255, 0, 0),
            description=f"{EMB_ALIASES}")
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        emb.set_footer(text=ctx.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emb)


    @commands.command(name = "help", aliases = ["h"])
    async def _help(self, ctx: commands.Context):
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(
            title = "HELP: ``Не забывайте про префикс '!'``",
            color=discord.Colour.from_rgb(255, 0, 0),
            description=f"{EMB_HELP}")
        # emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        # emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(name = "rainbow", aliases = ["rb"])
    async def _rainbow(self, ctx: commands.Context, variant="rnd", time=5.0):
        if 60.0 < time or time < 1.0:
            embed = discord.Embed(
                description=f"{ctx.author.mention}, границы скорости от 1 до 60 секунд, ты ввел {time}!",
                color=0x000000)
            time = 5
            await ctx.send(embed=embed)

        role = discord.utils.get(ctx.guild.roles, id=1139160276479004794)  # id-роли 1139160276479004794, тест 910544991464603679
        await ctx.author.add_roles(role)

        if variant == "off":
            embed = discord.Embed(description=f"Радуга у {ctx.author.mention} выключена!", color=0x000000)
            await ctx.send(embed=embed)
            await ctx.author.remove_roles(role)

        elif variant == "on":
            colours = [0xff0000, 0xff9f00, 0x72ff00, 0x00ff6d, 0x00acff, 0x0200ff, 0xc500ff, 0xff0053, 0xFA8072,
                       0xFF7F50,
                       0x00CED1, 0x800080, 0x696969]  # цвет в формате 0xHEX
            embed = discord.Embed(description=f"Радуга у {ctx.author.mention} включена!\nСкорость = {time} сек!",
                                  color=0x000000)
            await ctx.send(embed=embed)

            while variant == "on":
                await role.edit(colour=choice(colours))
                await asyncio.sleep(time)

        elif variant == "rnd":
            embed = discord.Embed(description=f"Радуга у {ctx.author.mention} включена!\nСкорость = {time} сек!",
                                  color=0x000000)
            await ctx.send(embed=embed)

            while variant == "rnd":
                await role.edit(colour=discord.Color(randint(0x000000, 0xFFFFFF)))
                await asyncio.sleep(time)


