import os
import time
import asyncio
import requests

try:
    import discord_self as discord
except ImportError:
    import discord

TOKEN = os.environ["DISCORD_USER_TOKEN"].strip()

raw_channel_id = os.environ["DISCORD_CHANNEL_ID"].strip().strip('"').strip("'")
CHANNEL_ID = int(raw_channel_id)

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"].strip()

print(f"🔧 Запускаюсь с CHANNEL_ID={CHANNEL_ID}")


def make_payload(author, content):
    return {
        "content": f"📨 **{author}**: {content}",
        "username": "Auto Joiner Logger",
    }


class SelfBot(discord.Client):
    def __init__(self):
        intents = None
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            intents.messages = True
        except Exception:
            intents = None

        if intents:
            super().__init__(intents=intents)
        else:
            super().__init__()

    async def on_ready(self):
        print(f"✅ Онлайн как {self.user}")
        ch = self.get_channel(CHANNEL_ID)
        if ch:
            print(f"📡 Найден канал #{ch.name} ({ch.id})")
        else:
            print(f"❌ Канал с ID {CHANNEL_ID} не найден!")

    async def on_message(self, msg):
        try:
            # 1) Фильтр по каналу (строго по id)
            if int(msg.channel.id) != CHANNEL_ID:
                return

            # 2) Игнор своих сообщений
            if hasattr(self.user, "id") and msg.author.id == self.user.id:
                return

            content = (msg.content or "").strip()
            author = str(msg.author)

            print(f"📨 {author}: {content}")

            payload = make_payload(author, content)

            # 3) Не блокируем event loop: HTTP в thread
            await asyncio.to_thread(requests.post, WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"⚠️ Ошибка в on_message: {e}")


if __name__ == "__main__":
    bot = SelfBot()
    while True:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"💥 Крах: {e}")
            time.sleep(10)
