import discord
import requests
import os
import sys

# ========== СЕКРЕТЫ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
TOKEN = os.environ.get("DISCORD_USER_TOKEN")        # Токен твоего аккаунта
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", 0))  # ID канала
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")  # URL вебхука

# Проверка, что всё на месте
if not all([TOKEN, CHANNEL_ID, WEBHOOK_URL]):
    print("❌ Не хватает секретов!")
    print("Нужны: DISCORD_USER_TOKEN, DISCORD_CHANNEL_ID, DISCORD_WEBHOOK_URL")
    sys.exit(1)

class SelfBot(discord.Client):
    async def on_ready(self):
        print(f'✅ Залетели как: {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            print(f'📡 Слежу за каналом: #{channel.name}')
        else:
            print(f'❌ Канал с ID {CHANNEL_ID} не найден!')

    async def on_message(self, message):
        # Игнорируем свои сообщения и другие каналы
        if message.author == self.user or message.channel.id != CHANNEL_ID:
            return

        print(f'📨 {message.author}: {message.content}')
        
        # Шлём напрямую в вебхук
        self.send_to_webhook(message)

    def send_to_webhook(self, message):
        """Отправляет лог в Discord Webhook"""
        data = {
            "content": f"📨 **{message.author.name}**: {message.content}",
            "username": "Auto Joiner Logger"  # Имя вебхука (можно любое)
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=data)
            if response.status_code == 204:
                print(f'✅ Отправлено в вебхук')
            else:
                print(f'❌ Ошибка: {response.status_code}')
        except Exception as e:
            print(f'❌ Не отправилось: {e}')

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    bot = SelfBot()
    bot.run(TOKEN)
