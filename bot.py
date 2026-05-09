import os
import time
import asyncio
import requests
import discord

# ---------- НАСТРОЙКИ ----------
TOKEN = os.environ["DISCORD_USER_TOKEN"]               # секрет из GitHub Actions
INT_CHANNEL_ID = 1401775181025775738
WEBHOOK_URL = "https://discord.com/api/webhooks/1462757260659916890/RDh5763wE364uxKkVkXt_lyslZ8nwubNIuJutkntFBbyTjI-6bgd9CChrVccpASv6f-b"

# ---------- ОБРЕЗКА ----------
def truncate(text: str, max_len: int = 1500) -> str:
    return text if len(text) <= max_len else text[:max_len-3] + "..."

# ---------- ИНТЕНТЫ ----------
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

class Forwarder(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged as {self.user}")

    async def on_message(self, msg):
        # Фильтры
        if not self.user or not msg.channel or msg.channel.id != INT_CHANNEL_ID:
            return
        if msg.author.id == self.user.id:
            return
        text = truncate(msg.content or "")
        if not text:
            return

        author = str(msg.author)
        print(f"📨 {author}: {text}")

        # Отправка в вебхук
        payload = {
            "content": f"📨 **{author}**: {text}",
            "username": "FestoLogs"
        }
        try:
            r = await asyncio.to_thread(
                requests.post, WEBHOOK_URL, json=payload, timeout=10
            )
            print(f"   -> Webhook: {r.status_code}")
        except Exception as e:
            print(f"   -> Webhook error: {e}")

if __name__ == "__main__":
    bot = Forwarder(intents=intents)
    # Запуск с обработкой фатальных ошибок
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ FATAL: Invalid token. Check DISCORD_USER_TOKEN secret.")
        exit(1)
    except Exception as e:
        # Временный сбой – перезапуск
        print(f"💥 Crash: {e}. Restarting in 15s...")
        time.sleep(15)
