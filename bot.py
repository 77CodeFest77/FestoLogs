import discord
import requests
import json
import os

# Берем данные из секретов GitHub (чтобы не палить в коде)
TOKEN = os.getenv('DISCORD_TOKEN')
FIREBASE_URL = 'https://serveraj-eb052-default-rtdb.firebaseio.com/last_job.json'
TARGET_CHANNEL_ID = 1401775181025775738

class FirebaseRelay(discord.Client):
    async def on_ready(self):
        print(f'✅ Бот запущен на GitHub Actions! {self.user}')

    async def on_message(self, message):
        if message.channel.id == TARGET_CHANNEL_ID:
            full_text = ""
            if message.content: full_text += message.content + "\n"
            if message.embeds:
                for e in message.embeds:
                    if e.description: full_text += e.description + "\n"
                    for f in e.fields: full_text += f"{f.name}: {f.value}\n"
            
            if full_text.strip():
                try:
                    payload = {"text": full_text, "time": str(message.created_at)}
                    requests.put(FIREBASE_URL, data=json.dumps(payload))
                    print("📡 Данные успешно отправлены в Firebase!")
                except Exception as e:
                    print(f"❌ Ошибка Firebase: {e}")

client = FirebaseRelay()
client.run(TOKEN)
