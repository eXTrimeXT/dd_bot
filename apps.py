from conf import *

class Apps(commands.Cog):
    def __init__(self, bot: commands.Bot):
        logger("Apps", "__init__")


    @commands.command(name="app", aliases=["приложение"])
    async def _app(self, ctx: commands.Context, id_app):
        target_app_id = 0
        if id_app == "1":
            target_app_id = 755600276941176913 # Youtube
        elif id_app == "2":
            target_app_id = 755827207812677713 # Poker Night
        elif id_app == "3":
            target_app_id = 832012774040141894 # Chess
        else:
            await ctx.send("Вы выбрали неверный номер! Их всего 3. Смотри `!help`")

        if target_app_id != 0:
            data = {
                "max_age": 86400,
                "max_uses": 0,
                "target_application_id": target_app_id,
                "target_type": 2,
                "temporary": False,
                "validate": None
            }
            headers = {
                "Authorization": f"Bot {TOKEN}",
                "Content-Type": "application/json"
            }
            if (ctx.author.voice is not None) and (ctx.author.voice.channel is not None):
                channel = ctx.author.voice.channel.id
                response = requests.post(f"https://discord.com/api/v8/channels/{channel}/invites", data=json.dumps(data), headers=headers)
                link = json.loads(response.content)
                await ctx.send(f"https://discord.com/invite/{link['code']}")
            else:
                await ctx.send("Зайдите в голосовой канал!")