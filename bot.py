import os
import sys
import time
import asyncio
import requests

try:
    import discord_self as discord
except ImportError:
    import discord

# ====== НАСТРОЙКИ: ЗАПОЛНИ СЕЙЧАС ======
CHANNEL_ID = 1401775181025775738
WEBHOOK_URL = "https://discord.com/api/webhooks/1462757260659916890/RDh5763wE364uxKkVkXt_lyslZ8nwubNIuJutkntFBbyTjI-6bgd9CChrVccpASv6f-b"
# =======================================

TOKEN = os.environ.get("DISCORD_USER_TOKEN", "").strip()
if not TOKEN:
    print("❌ DISCORD_USER_TOKEN не задан в GitHub Secrets.")
    sys.exit(1)

if not WEBHOOK_URL:
    print("❌ WEBHOOK_URL не задан в коде.")
    sys.exit(1)

if not CHANNEL_ID:
    print("❌ CHANNEL_ID не задан в коде.")
    sys.exit(1)

INT_CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True


def truncate(s: str, n: int = 1900) -> str:
    s = s or ""
    if len(s) <= n:
        return s
    return s[:n] + "…"


class SelfBot(discord.Client):
    async def on_ready(self):
        print(f"✅ Online as: {self.user} (id={self.user.id})")

        ch = self.get_channel(INT_CHANNEL_ID)
        if ch:
            name = getattr(ch, "name", "???")
            print(f"📡 Канал найден: #{name} ({ch.id})")
        else:
            print(
                f"❌ Канал с ID {INT_CHANNEL_ID} не найден в cache. "
                "Возможно, нужно другое id (например, thread id)."
            )

    async def post_to_webhook(self, payload: dict):
        try:
            r = await asyncio.to_thread(
                requests.post, WEBHOOK_URL, json=payload, timeout=15
            )
            print(f"   -> Webhook: {r.status_code}")
        except Exception as e:
            print(f"   -> Webhook error: {e}")

    async def on_message(self, msg):
        try:
            if not getattr(msg, "channel", None):
                return
            if not getattr(msg, "author", None):
                return
            if not self.user:
                return

            # Фильтр только нужного канала
            if int(msg.channel.id) != INT_CHANNEL_ID:
                return

            # Не форвардим свои сообщения self-bot'а
            if msg.author.id == self.user.id:
                return

            content = truncate(getattr(msg, "content", "") or "").strip()
            if not content:
                return

            author = str(msg.author)
            print(f"📨 {author} ({msg.author.id}): {content}")

            payload = {
                "content": f"📨 **{author}**: {content}",
                "username": "Auto Joiner Logger",
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
