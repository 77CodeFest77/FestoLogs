import os
import time
import requests

try:
    import discord_self as discord
except ImportError:
    import discord


def require_env(name: str) -> str:
    value = os.environ.get(name, "")
    value = value.strip().strip('"').strip("'")
    if not value:
        raise RuntimeError(f"Пустая переменная окружения: {name}")
    return value


TOKEN = require_env("DISCORD_USER_TOKEN")

raw_channel_id = require_env("DISCORD_CHANNEL_ID")
try:
    CHANNEL_ID = int(raw_channel_id)
except ValueError:
    raise RuntimeError(
        f"DISCORD_CHANNEL_ID не является числом: {raw_channel_id!r}"
    )

WEBHOOK_URL = require_env("DISCORD_WEBHOOK_URL")

print(f"🔧 Запускаюсь с CHANNEL_ID={CHANNEL_ID}")
print("🔧 Проверка env: OK (токен/вебхук не печатаю)")


intents = None
try:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True
except Exception:
    intents = None


class SelfBot(discord.Client):
    def __init__(self):
        if intents is not None:
            super().__init__(intents=intents)
        else:
            super().__init__()

    async def on_ready(self):
        print(f"✅ Онлайн как: {self.user}")
        ch = self.get_channel(CHANNEL_ID)
        if ch:
            print(f"📡 Канал: #{getattr(ch, 'name', '???')} ({ch.id})")
        else:
            print(f"❌ Канал с ID {CHANNEL_ID} не найден в кэше")

    async def on_message(self, msg):
        if not getattr(self, "user", None):
            return

        # игнор своих
        if msg.author and msg.author.id == self.user.id:
            return

        # фильтр по каналу
        if not getattr(msg, "channel", None):
            return
        if int(msg.channel.id) != CHANNEL_ID:
            return

        content = (msg.content or "").strip()
        if not content:
            return

        print(f"📨 {msg.author}: {content[:120]}")

        payload = {
            "content": f"📨 **{msg.author.name}**: {content}",
            "username": "Auto Joiner Logger",
        }

        try:
            r = await self.loop.run_in_executor(
                None, lambda: requests.post(WEBHOOK_URL, json=payload, timeout=15)
            )
            print(f"   -> Webhook: {r.status_code}")
        except Exception as e:
            print(f"   -> Webhook ошибка: {e}")


if __name__ == "__main__":
    bot = SelfBot()
    while True:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"💥 Крах: {e}")
            time.sleep(10)
