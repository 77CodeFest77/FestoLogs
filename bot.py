import os
import sys
import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks

# ---------- КОНФИГУРАЦИЯ ----------
TOKEN = os.environ.get("DISCORD_USER_TOKEN", "")
SOURCE_CHANNEL_ID = 1401775181025775738
WEBHOOK_URL = "https://discord.com/api/webhooks/1462757260659916890/RDh5763wE364uxKkVkXt_lyslZ8nwubNIuJutkntFBbyTjI-6bgd9CChrVccpASv6f-b"

if not TOKEN:
    print("❌ DISCORD_USER_TOKEN MISSING")
    sys.exit(1)

# ---------- ЛОГИКА FESTKA ----------
class FestkaForwarder(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    async def setup_hook(self):
        # Инициализация асинхронной сессии при запуске
        self.session = aiohttp.ClientSession()
        self.check_connection.start()

    async def on_ready(self):
        print(f"--- Festka System Online ---")
        print(f"Logged as: {self.user}")
        print(f"Monitoring ID: {SOURCE_CHANNEL_ID}")
        print(f"----------------------------")

    @tasks.loop(minutes=5)
    async def check_connection(self):
        if self.is_closed():
            print("🔄 Reconnecting...")

    async def send_to_webhook(self, author, content, attachments=None):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        
        webhook = discord.Webhook.from_url(WEBHOOK_URL, session=self.session)
        
        # Создание эмбеда для чистого и красивого лога
        embed = discord.Embed(
            description=content or "*Пустое сообщение*",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(
            name=str(author), 
            icon_url=author.avatar.url if author.avatar else None
        )
        
        if attachments:
            file_list = "\n".join([att.url for att in attachments])
            embed.add_field(name="Вложения", value=file_list)

        try:
            await webhook.send(
                embed=embed,
                username="Festka Logger",
                avatar_url="https://i.imgur.com/8N7S6fC.png"
            )
        except Exception as e:
            print(f"⚠️ Webhook Error: {e}")

    async def on_message(self, message):
        # Фильтрация: только нужный канал и игнор самого себя
        if message.channel.id != SOURCE_CHANNEL_ID:
            return
        
        if message.author.id == self.user.id:
            return

        print(f"📩 Log captured from {message.author}")
        await self.send_to_webhook(message.author, message.content, message.attachments)

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    # Настройка интентов для работы с сообщениями (Self-bot/User-bot mode)
    intents = discord.Intents.default()
    intents.message_content = True 
    intents.messages = True
    intents.guilds = True

    client = FestkaForwarder(intents=intents)

    try:
        client.run(TOKEN)
    except discord.LoginFailure:
        print("❌ CRITICAL: Invalid Discord Token")
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
