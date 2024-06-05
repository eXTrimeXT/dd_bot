import asyncio
from async_timeout import timeout
import discord
from discord.ext import commands
from YTDLSource import YTDLSource, VoiceError
from SongQueue import SongQueue
from conf import logger


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
        self._volume = 1.0
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


    # Устанавливает статус бота
    async def set_status(self, text: str):
        logger("set_status", f"{text}")
        await self.bot.change_presence(activity=discord.CustomActivity(name=f'{text}'))


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
                    # await self.set_status("Отдыхаю...")
                    # Добавить выкл радуги

                self.current.source.volume = self._volume
                await self.current.source.channel.send(embed=self.current.create_embed(self.bot))
                # await self.set_status(f"Слушаю {self.current.source}")
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
            # await self.set_status("Отдыхаю...")
        logger("VoiceState stop", "END")