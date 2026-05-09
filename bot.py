import os
import time
import asyncio
import requests
import discord

# ---------- настройки ----------
TOKEN = os.environ["DISCORD_USER_TOKEN"]          # токен – только из переменной окружения!
INT_CHANNEL_ID = 1401775181025775738
WEBHOOK_URL = "https://discord.com/api/webhooks/1462757260659916890/RDh5763wE364uxKkVkXt_lyslZ8nwubNIuJutkntFBbyTjI-6bgd9CChrVccpASv6f-b"

# ---------- обрезка длинных сообщений ----------
def truncate(text: str, max_len: int = 1500) -> str:
    """Обрезает текст до max_len символов, добавляя многоточие."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."

# ---------- интенты ----------
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True   # обязательно для чтения содержимого сообщений

class SelfBot(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        channel = self.get_channel(INT_CHANNEL_ID)
        if channel:
            print(f"📡 Channel found: #{getattr(channel, 'name', '???')} ({channel.id})")
        else:
            print(f"⚠️ Channel {INT_CHANNEL_ID} not in cache; will still try by ID.")

    async def post_to_webhook(self, payload: dict):
        """Отправка payload в вебхук через отдельный поток (requests)."""
        def do_post():
            return requests.post(WEBHOOK_URL, json=payload, timeout=15)

        try:
            r = await asyncio.to_thread(do_post)
            print(f"   -> Webhook: {r.status_code}")
        except Exception as e:
            print(f"   -> Webhook error: {e}")

    async def on_message(self, msg):
        try:
            # Ждём, пока бот полностью загрузится
            if not self.user:
                return

            # Проверяем, что сообщение из нужного канала
            if not msg.channel or msg.channel.id != INT_CHANNEL_ID:
                return

            # Не пересылаем свои собственные сообщения
            if msg.author.id == self.user.id:
                return

            # Текст сообщения
            content = truncate(msg.content or "")
            if not content:
                return

            author = str(msg.author)
            print(f"📨 {author} ({msg.author.id}): {content}")

            payload = {
                "content": f"📨 **{author}**: {content}",
                "username": "FestoLogs Bot",
            }
            await self.post_to_webhook(payload)

        except Exception as e:
            print(f"⚠️ on_message error: {e}")

if __name__ == "__main__":
    bot = SelfBot(intents=intents)

    while True:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"💥 Crash: {e}")
            time.sleep(10)
