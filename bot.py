import os
import sys
import time
import asyncio
import requests
import discord

# ---------- НАСТРОЙКИ ----------
TOKEN = os.environ.get("DISCORD_USER_TOKEN", "")
if not TOKEN:
    print("❌ DISCORD_USER_TOKEN не задан в переменных окружения.")
    sys.exit(1)

INT_CHANNEL_ID = 1401775181025775738
WEBHOOK_URL = "https://discord.com/api/webhooks/1462757260659916890/RDh5763wE364uxKkVkXt_lyslZ8nwubNIuJutkntFBbyTjI-6bgd9CChrVccpASv6f-b"

# ---------- ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ТОКЕНА ----------
print("🔍 Проверяю токен...")
headers = {"Authorization": TOKEN}
try:
    r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Токен действителен! Пользователь: {data['username']}#{data['discriminator']} (ID: {data['id']})")
    elif r.status_code == 401:
        print("❌ Токен НЕВЕРЕН (401 Unauthorized).")
        print("   Причина: токен просрочен, отозван или это токен бота, а не пользователя.")
        sys.exit(1)
    else:
        print(f"⚠️ Неожиданный ответ: {r.status_code} {r.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    sys.exit(1)

# ---------- ОСТАЛЬНОЙ КОД ----------
def truncate(text: str, max_len: int = 1500) -> str:
    return text if len(text) <= max_len else text[:max_len-3] + "..."

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

class Forwarder(discord.Client):
    async def on_ready(self):
        print(f"✅ Бот запущен как {self.user}")

    async def on_message(self, msg):
        if not self.user or not msg.channel or msg.channel.id != INT_CHANNEL_ID:
            return
        if msg.author.id == self.user.id:
            return
        text = truncate(msg.content or "")
        if not text:
            return

        author = str(msg.author)
        print(f"📨 {author}: {text}")

        payload = {
            "content": f"📨 **{author}**: {text}",
            "username": "FestoLogs"
        }
        try:
            r = await asyncio.to_thread(requests.post, WEBHOOK_URL, json=payload, timeout=10)
            print(f"   -> Webhook: {r.status_code}")
        except Exception as e:
            print(f"   -> Webhook error: {e}")

if __name__ == "__main__":
    while True:
        bot = Forwarder(intents=intents)
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("❌ Критическая ошибка входа. Проверь токен.")
            sys.exit(1)
        except Exception as e:
            print(f"💥 Сбой: {e}. Перезапуск через 15 секунд...")
            time.sleep(15)
