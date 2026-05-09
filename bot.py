import os
import sys
import time
import asyncio
import requests
import discord

# ---------- настройки ----------
TOKEN = os.environ["DISCORD_USER_TOKEN"]          # токен из секрета
INT_CHANNEL_ID = 1401775181025775738
WEBHOOK_URL = "https://discord.com/api/webhooks/1462757260659916890/RDh5763wE364uxKkVkXt_lyslZ8nwubNIuJutkntFBbyTjI-6bgd9CChrVccpASv6f-b"

# ---------- обрезка длинных сообщений ----------
def truncate(text: str, max_len: int = 1500) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."

# ---------- интенты ----------
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

class SelfBot(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        channel = self.get_channel(INT_CHANNEL_ID)
        if channel:
            print(f"📡 Channel found: #{getattr(channel, 'name', '???')} ({channel.id})")
        else:
            print(f"⚠️ Channel {INT_CHANNEL_ID} not in cache; will try by ID.")

    async def post_to_webhook(self, payload: dict):
        def do_post():
            return requests.post(WEBHOOK_URL, json=payload, timeout=15)
        try:
            r = await asyncio.to_thread(do_post)
            print(f"   -> Webhook: {r.status_code}")
        except Exception as e:
            print(f"   -> Webhook error: {e}")

    async def on_message(self, msg):
        try:
            if not self.user:
                return
            if not msg.channel or msg.channel.id != INT_CHANNEL_ID:
                return
            if msg.author.id == self.user.id:
                return
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

async def main():
    bot = SelfBot(intents=intents)
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure as e:
        print(f"❌ LOGIN FAILED: {e}")
        print("Check your token. It must be a USER token (not bot).", file=sys.stderr)
        sys.exit(1)
    except discord.HTTPException as e:
        if e.status == 401:
            print("❌ Unauthorized (401). Token invalid or revoked.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"❌ HTTP error: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Перезапуск только при временных ошибках (разрыв соединения и т.п.)
    while True:
        try:
            asyncio.run(main())
        except SystemExit:
            raise   # критическая ошибка – выходим совсем
        except Exception as e:
            print(f"💥 Crash: {e}. Restarting in 15s...")
            time.sleep(15)
