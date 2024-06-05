import discord
from random import *
from YTDLSource import YTDLSource


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def get_requester(self):
        return self.requester

    def create_embed(self, bot):
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
                .set_thumbnail(url=self.source.thumbnail)  # Миниатюра
                .set_author(name=self.requester.name, icon_url=self.requester.avatar))
        return embed