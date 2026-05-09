import os
import time
import asyncio
import requests
import sys

try:
    import discord_self as discord
except ImportError:
    import discord


TOKEN = os.environ.get("DISCORD_USER_TOKEN", "").strip()
raw_channel_id = os.environ.get("DISCORD_CHANNEL_ID", "0").strip()
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()

if not TOKEN or not raw_channel_id or not WEBHOOK_URL:
    print("❌ Не хватает секретов!")
    print(
        "Нужны: DISCORD_USER_TOKEN, DISCORD_CHANNEL_ID, DISCORD_WEBHOOK_URL"
    )
    sys.exit(1)

raw_channel_id = raw_channel_id.strip().strip('"').strip("'")
CHANNEL_ID = int(raw_channel_id)

print(f"🔧 Запускаюсь с CHANNEL_ID={CHANNEL_ID}")


def build_payload(author_name: str, content: str) -> dict:
    # В webhook "content" лучше отправлять строкой.
    return {
        "content": f"📨 **{author_name}**: {content}",
        "username": "Auto Joiner Logger",
    }


class SelfBot(discord.Client):
    async def on_ready(self):
        print(f"✅ Онлайн как: {self.user} (id={self.user.id})")

        ch = self.get_channel(CHANNEL_ID)
        if ch:
            print(f"📡 Слежу за каналом: #{getattr(ch, 'name', '???')} ({ch.id})")
        else:
            print(f"❌ Канал с ID {CHANNEL_ID} не найден!")

    async def on_message(self, msg):
        # self.user может быть None в самом начале
        if not getattr(self, "user", None):
            return

        # 1) Канал
        if int(msg.channel.id) != CHANNEL_ID:
            return

        # 2) Не форвардим сообщения самого бота
        if msg.author and msg.author.id == self.user.id:
            return

        content = (msg.content or "").strip()
        if not content:
            return

        print(f"📨 {msg.author}: {content[:120]}")

        payload = build_payload(str(msg.author), content)

        async def post_webhook():
            try:
                r = requests.post(WEBHOOK_URL, json=payload, timeout=15)
                print(f"   -> Webhook: {r.status_code}")
            except Exception as e:
                print(f"   -> Webhook ошибка: {e}")

        # HTTP без блокировки event loop
        await asyncio.to_thread(post_webhook)


bot = SelfBot()
while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"💥 Крах: {e}")
        time.sleep(10)
