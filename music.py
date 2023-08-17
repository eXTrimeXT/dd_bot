from conf import *

# Молчание бесполезных сообщений об ошибках
youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': False,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))  # day hour min sec
        self.sec_duration = int(data.get('duration')) # sec
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.stream_url = data.get('url')


    def __str__(self):
        return f"**{self.title}**"


    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=True)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f"Не удалось найти ничего подходящего `{search}`")

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(f"Не удалось найти ничего подходящего `{search}`")

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f"Не удалось получить `{webpage_url}`")

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(f"Не удалось получить совпадений для `{webpage_url}`")

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)


    @classmethod
    async def search_source(self, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None, bot=None):
        self.bot = bot
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        self.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(self.ytdl.extract_info, self.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        self.search = {}
        self.search["title"] = f"Результаты поиска для:\n**{search}**"
        self.search["type"] = 'rich'
        self.search["color"] = 100000 # 7506394
        #self.search["author"] = {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar_url}', 'icon_url': f'{ctx.author.avatar_url}'}

        lst = []
        count = 0
        e_list = []
        for e in info['entries']:
            VId = e.get('id')
            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
            lst.append(f'`{count + 1}.` [{e.get("title")}]({VUrl})\n')
            count += 1
            e_list.append(e)

        lst.append("**Введите число, чтобы сделать выбор\nВведите `cancel` или `отмена` чтобы отменить\nЧерез 1 минуту команда будет отменена!**")
        self.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(self.search)
        await ctx.send(embed=em, delete_after=60.0)

        def check(msg):
            return msg.content.isdigit() == True and msg.channel == channel or msg.content == "cancel" or msg.content == "отмена"

        try:
            m = await self.bot.wait_for("message", check=check, timeout=60.0)

        except asyncio.TimeoutError:
            rtrn = 'timeout'

        else:
            if m.content.isdigit() == True:
                sel = int(m.content)
                if 0 < sel <= 10:
                    for key, value in info.items():
                        if key == 'entries':
                            """data = value[sel - 1]"""
                            VId = e_list[sel - 1]['id']
                            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
                            partial = functools.partial(self.ytdl.extract_info, VUrl, download=False)
                            data = await loop.run_in_executor(None, partial)
                    rtrn = self(ctx, discord.FFmpegPCMAudio(data['url'], **self.FFMPEG_OPTIONS), data=data)
                else:
                    rtrn = 'sel_invalid'
            elif m.content == "cancel" or m.content == "отмена":
                rtrn = 'cancel'
            else:
                rtrn = 'sel_invalid'
        return rtrn


    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            duration = []

            if days >= 0:
                duration.append(f"{days}")
            if hours >= 0:
                duration.append(f"{hours}")
            if minutes >= 0:
                duration.append(f"{minutes}")
            if seconds >= 0:
                duration.append(f"{seconds}")

            value = ':'.join(duration)

        elif duration == 0:
            value = "**СТРИМ**"
            # [hls @ 000001d40fc95340] skipping 1 segments ahead, expired from playlists

        return value


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def get_requester(self):
        return self.requester

    def create_embed(self, bot):
        logger("Song create_embed", "CREATED!")
        embed = (discord.Embed(
            title="Опа, смотри что играет!",
            url = self.source.url,
            description=f"```css\n{self.source.title}\n```",
            colour=discord.Colour.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255)))
                .add_field(name='Запросил', value=self.requester.mention)
                .add_field(name=f'Время трека', value=self.source.duration)
                .add_field(name='Просмотров', value=self.source.views)
                .add_field(name='Автор видео', value=f"[{self.source.uploader}]({self.source.uploader_url})")
                .add_field(name='Лайков', value=self.source.likes)
                .add_field(name='Дата публикации', value=self.source.upload_date)
                .set_thumbnail(url=self.source.thumbnail))  # Миниатюра
                # .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


# # Устанавливает статус бота
async def set_status(bot, text: str):
    logger("set_status", f"{text}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{text}"))


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx
        self.current = None
        self.now = None
        self.stream_url = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True
        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()
        self.audio_player = bot.loop.create_task(self.audio_player_task())
        logger("VoiceState", "__init__")

    def __del__(self):
        logger("VoiceState", "__del__")
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        logger(f"VoiceState", "is_playing")
        return self.voice and self.current


    # Постарайтесь получить следующую песню в течение X минут. Если ни одна песня не будет добавлена в очередь вовремя,
    # проигрыватель отключится по причинам производительности.
    async def audio_player_task(self):
        while True:
            logger("VoiceState audio_player_task", f"START")
            self.next.clear()

            logger("VoiceState audio_player_task", f"loop = {self.loop}")
            if self.loop == False:
                try:
                    async with timeout(60):
                        self.current = await self.songs.get()
                        self.stream_url = self.current.source.stream_url

                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    await set_status(self.bot, "Отдыхаю...")
                    # Добавить выкл радуги

                self.current.source.volume = self._volume
                await self.current.source.channel.send(embed=self.current.create_embed(self.bot))
                await set_status(self.bot, f"{self.current.source}")
                # Добавить вкл радуги

                self.voice.play(self.current.source, after=self.play_next_song)

            # Если песня зациклена
            else:
                self.now = discord.FFmpegPCMAudio(executable=self.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)
            await self.next.wait()
            logger("VoiceState audio_player_task", f"END")


    def play_next_song(self, error=None):
        logger("VoiceState play_next_song", "START")
        if error:
            raise VoiceError(str(error))

        self.next.set()
        self.current.source = None
        logger("VoiceState play_next_song", "END")


    def skip(self):
        logger("VoiceState skip", "START")
        self.skip_votes.clear()
        if self.is_playing:
            self.voice.stop()
        logger("VoiceState skip", "END")


    async def stop(self):
        logger("VoiceState stop", "START")
        self.songs.clear()
        self.now = None
        self.stream_url = None
        if self.voice:
            logger("VoiceState stop", "if")
            await self.voice.disconnect()
            self.voice = None
        logger("VoiceState stop", "END")


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
#         if str(error).find("your age"):
#             await ctx.send("Бот не может включать треки :underage:!!!")
#         else:
#             print(f"cog_command_error : ОШИБКА: {str(error)}")
        print(f"Ошибка: {str(error)}")
        await ctx.send(f"Код ошибки: {str(error)}")
        await ctx.send(f"Появилась ошибка, возможно вы ввели команду неправильно!")



    @commands.Cog.listener()
    async def on_message(self, message):
        if IS_MESSAGE_LOG:
            if message.author.id != bot.user.id:
                print(f"{message.guild}/{message.channel}/{message.author.name}>{message.content}")
                if message.embeds:
                    print(message.embeds[0].to_dict())


    # Бот входит в голосовой чат
    @commands.command(name="join", aliases=["войди"], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        logger("Music join", "START")
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
        ctx.voice_state.voice = await destination.connect()
        logger("Music join", "END")


    # Вызывает бота в голосовой канал. Если канал не указан, он присоединяется к вашему каналу.
    # @commands.has_permissions(manage_guild=True)
    @commands.command(name="invite", aliases=["вызвать"])
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
        await set_status(self.bot, "Отдыхаю...")
        if not ctx.voice_state.voice:
            return await ctx.send('Бот и так не подключен. Зачем его кикать?')
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]
        logger("Music leave", "END")


    # Устанавливает громкость плеера
    @commands.command(name="volume", aliases=["громкость"])
    @commands.has_permissions(administrator=True)
    async def _volume(self, ctx: commands.Context, volume: int):
        logger("Music volume", "START")
        if not ctx.voice_state.is_playing:
            return await ctx.send("В данный момент ничего не воспроизводится.")

        if 0 > volume > 100:
            return await ctx.send("Громкость должна быть от 0 до 100")

        ctx.voice_state.volume = volume / 100
        await ctx.send(f"Установлена громкость: {volume}")
        logger("Music volume", "END")


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
    @commands.command(name="skip", aliases=["скип"])
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


    # Показывает очередь игрока. При желании вы можете указать страницу для отображения. Каждая страница содержит 10 элементов.
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
    @commands.command(name="loop", aliases=["цикл"])
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


    @commands.command(name="playalias", aliases=["мш"])
    async def _play_alias(self, ctx: commands.Context, variable: str):
        logger("PLAY_MIYAGI", "START")
        url = ""
        if variable == "м":
            url = "https://www.youtube.com/watch?v=v4dzXyqO1tY&t=11s"
        elif variable == "ш":
            url = "https://www.youtube.com/watch?v=M8QnkbRpqr8"

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send(f"Произошла ошибка при обработке этого запроса: {str(e)}")
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send(f"Добавлено в очередь {str(source)}")
        logger("PLAY_MIYAGI", "END")


    # Играет песню. Если уже играет трек, то другие треки будут помещены в очередь до тех пор, пока другие песни не закончат играть.
    # Эта команда автоматически выполняет поиск с разных сайтов, если URL-адрес не указан.
    @commands.command(name="pl", aliases=["играй"])
    async def _play(self, ctx: commands.Context, *, search: str):
        logger("Music play", "START")
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send(f"Произошла ошибка при обработке этого запроса: {str(e)}")
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send(f"Добавлено в очередь {str(source)}")
        logger("Music play", "END")


    # Выполняет поиск на YouTube. Он возвращает вставку первых 10 результатов, собранных с YouTube.
    # Затем пользователь может выбрать одно из названий, набрав число в чате или они могут отменить, набрав «отменить» в чате.
    # На каждый заголовок в списке можно щелкнуть как ссылку.
    @commands.command(name="search", aliases=["ищи"])
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
                        await ctx.invoke(self._join)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send(f"Добавлено в очередь {str(source)}")
        logger("Music search", "END")


    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Вы не подключены ни к одному из голосовых каналов.")
            raise commands.CommandError("Вы не подключены ни к одному из голосовых каналов.")

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send("Бот уже находится в голосовом канале.")
                raise commands.CommandError("Бот уже находится в голосовом канале.")
        logger("Music ensure_voice_state", "END")
