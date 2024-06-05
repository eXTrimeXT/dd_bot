from async_timeout import timeout
import discord
from discord.ext import commands
from random import *
import yt_dlp as youtube_dl

from Song import Song
from VoiceState import VoiceState
from YTDLSource import YTDLSource, VoiceError, YTDLError
from conf import logger, check_log_file, IS_MESSAGE_LOG, bot, PATH_LOG



class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        logger("Music", "__init__")


    def get_voice_state(self, ctx: commands.Context):
        logger("Music get_voice_state", "START")
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        logger("Music get_voice_state", "END")
        return state


    def cog_unload(self):
        logger("Music", "cog_unload")
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())


    def cog_check(self, ctx: commands.Context):
        logger("Music", "cog_check")
        if not ctx.guild:
            raise commands.NoPrivateMessage("Эта команда не используется в ЛС")
        return True


    async def cog_before_invoke(self, ctx: commands.Context):
        logger("Music", "cog_before_invoke")
        ctx.voice_state = self.get_voice_state(ctx)


    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        print(f"Ошибка: {str(error)}")
        await ctx.send(f"Ошибка: {str(error)}")
        await ctx.send(f"Появилась ошибка, возможно вы ввели команду неправильно!")


    @commands.Cog.listener()
    async def on_message(self, message):
        if IS_MESSAGE_LOG:
            if message.author.id != bot.user.id:
                log_message = f"{message.guild}/{message.channel}/{message.author.name}>{message.content}"
                print(log_message)
                with open(PATH_LOG, "a", encoding="utf-8") as file:
                    file.write(log_message+"\n")
                check_log_file()
                if message.embeds:
                    print(message.embeds[0].to_dict())


    # Вызывает бота в голосовой канал. Если канал не указан, он присоединяется к вашему каналу.
    # @commands.has_permissions(manage_guild=True)
    @commands.command(name="invite", aliases=["вызвать"], invoke_without_subcommand=True)
    async def _invite(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        logger("Music invite", "START")
        if not channel and not ctx.author.voice:
            raise VoiceError('Вы не подключены к голосовому каналу и не указали канал для присоединения.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
        ctx.voice_state.voice = await destination.connect()
        logger("Music invite", "END")


    # Очищает очередь и покидает голосовой канал
    # @commands.has_permissions(administrator=True)
    @commands.command(name="leave", aliases=["выгнать"])
    async def _leave(self, ctx: commands.Context):
        logger("Music leave", "START")
        if not ctx.voice_state.voice:
            return await ctx.send('Бот и так не подключен. Зачем его кикать?')
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]
        await ctx.send("Бот отключился.")
        logger("Music leave", "END")


    # Отображает песню, которая воспроизводится в данный момент
    @commands.command(name="now", aliases=["сейчас"])
    async def _now(self, ctx: commands.Context):
        try:
            logger("Music now", "START")
            embed = ctx.voice_state.current.create_embed(self.bot)
            if ctx.voice_state.loop:
                await ctx.send(f"Зациклен трек ✅")

            await ctx.send(embed=embed)
            logger("Music now", "END")
        except:
            await ctx.send("``В данный момент ничего не играет``")


    # Приостанавливает воспроизводимую в данный момент песню
    @commands.command(name = "pause", aliases = ["пауза"])
    async def _pause(self, ctx: commands.Context):
        logger("Music pause", "START")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')
        logger("Music pause", "END")


    # Возобновляет воспроизведение приостановленной в данный момент песни
    @commands.command(name='resume', aliases=["продолжить"])
    async def _resume(self, ctx: commands.Context):
        logger("Music resume", "START")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')
        logger("Music resume", "END")


    # Останавливает воспроизведение песни и очищает очередь
    @commands.command(name="stop", aliases=["стоп"])
    async def _stop(self, ctx: commands.Context):
        logger("Music stop", "START")
        ctx.voice_state.songs.clear()
        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')
        logger("Music stop", "END")


    # Проголосуйте, чтобы пропустить песню.
    # Запрашивающая сторона может автоматически пропустить.
    # Для пропуска песни необходимо 3 голоса.
    @commands.command(name="skip", aliases=["пропуск"])
    async def _skip(self, ctx: commands.Context):
        logger("Music skip", "START")
        if not ctx.voice_state.is_playing:
            return await ctx.send("Я сейчас не играю музыку...")

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send(f"Пропустить голосование **{total_votes}/3**")

        else:
            await ctx.send("Вы уже проголосовали за то, чтобы пропустить эту песню")

        logger("Music skip", "END")


    # Показывает очередь треков. При желании вы можете указать страницу для отображения. Каждая страница содержит 10 элементов.
    @commands.command(name="queue", aliases=["очередь"])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        logger("Music queue", "START")
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("``В очереди нет треков``")

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += f"`{i + 1}.` [**{song.source.title}**]({song.source.url})\n"

        embed = (discord.Embed(description=f"**{len(ctx.voice_state.songs)} Треки:**\n\n{queue}").set_footer(text=f"Страница {page}/{pages}"))
        await ctx.send(embed=embed)
        logger("Music queue", "END")


    # Перемешивает очередь
    @commands.command(name="shuffle", aliases=["перемешать"])
    async def _shuffle(self, ctx: commands.Context):
        logger("Music shuffle", "START")
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("В очереди нет треков")

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')
        logger("Music shuffle", "END")


    # Удаляет песню из очереди по заданному индексу
    @commands.command(name="remove", aliases=["удалить"])
    async def _remove(self, ctx: commands.Context, index: int):
        logger("Music remove", "START")
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("В очереди нет треков")

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')
        logger("Music remove", "END")


    # Зацикливает воспроизводимую в данный момент песню.
    # Вызовите эту команду еще раз, чтобы разблокировать песню.
    @commands.command(name="loop", aliases=["зациклить"])
    async def _loop(self, ctx: commands.Context):
        logger("Music loop", "START")
        if not ctx.voice_state.is_playing:
            return await ctx.send("В данный момент ничего не играет!")

        ctx.voice_state.loop = not ctx.voice_state.loop

        if ctx.voice_state.loop:
            await ctx.send(f"Зациклен трек: {ctx.voice_state.current.source}! ✅")
        else:
            await ctx.send("Зацикливание выключено! ❎")
        logger("Music loop", f"loop = {ctx.voice_state.loop}")
        logger("Music loop", "END")


    # Играет песню. Если уже играет трек, то другие треки будут помещены в очередь до тех пор, пока другие песни не закончат играть.
    # Эта команда автоматически выполняет поиск с разных сайтов, если URL-адрес не указан.
    @commands.command(name="play", aliases=["играй"])
    async def _play(self, ctx: commands.Context, *, search: str):
        logger("Music play", "START")
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send(f"Произошла ошибка при обработке этого запроса: {str(e)}")
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._invite)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send(f"Добавлено в очередь {str(source)}")
        logger("Music play", "END")


    # Выполняет поиск на YouTube. Он возвращает вставку первых 10 результатов, собранных с YouTube.
    # Затем пользователь может выбрать одно из названий, набрав число в чате или они могут отменить, набрав «отменить» в чате.
    # На каждый заголовок в списке можно щелкнуть как ссылку.
    @commands.command(name="search", aliases=["найди"])
    async def _search(self, ctx: commands.Context, *, search: str):
        logger("Music search", "START")
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(ctx, search, loop=self.bot.loop, bot=self.bot)
            except YTDLError as e:
                await ctx.send(f"Произошла ошибка при обработке этого запроса: {str(e)}")
            else:
                if source == 'sel_invalid':
                    await ctx.send(":x: **Неверный выбор**")
                elif source == "cancel":
                    await ctx.send(":white_check_mark: **Отмена**")
                elif source == "timeout":
                    await ctx.send(':alarm_clock: **Время вышло**')
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._invite)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send(f"Добавлено в очередь {str(source)}")
        logger("Music search", "END")


    @_invite.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("Вы не подключены ни к одному из голосовых каналов.")

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("Бот уже находится в голосовом канале.")
        logger("Music ensure_voice_state", "END")

