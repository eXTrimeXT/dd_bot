import asyncio
import functools
from async_timeout import timeout
import discord
from discord.ext import commands
from discord import opus
from discord import FFmpegPCMAudio
from random import *
import yt_dlp as youtube_dl

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


    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 1.0):
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
        self.search["author"] = {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar}', 'icon_url': f'{ctx.author.avatar}'}

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
        return value