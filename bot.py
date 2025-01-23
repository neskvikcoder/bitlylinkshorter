from pyrogram import Client, filters
import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем переменные окружения
TOKEN = os.getenv("TOKEN")
API_ID = int(os.getenv("API_ID", 12345))
API_HASH = os.getenv("API_HASH")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")

# Отладочные сообщения
print(f"TOKEN: {TOKEN}")
print(f"API_ID: {API_ID}")
print(f"API_HASH: {API_HASH}")
print(f"BITLY_TOKEN: {BITLY_TOKEN}")

# Заголовки для запросов к Bitly
headers = {
    'Authorization': f'Bearer {BITLY_TOKEN}',
    'Content-Type': 'application/json',
}

# Инициализация клиента Pyrogram
app = Client("bitlybot", bot_token=TOKEN, api_id=API_ID, api_hash=API_HASH)

# Обработчик команды /start
@app.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    await message.reply_text(
        f"Hello {message.from_user.first_name}\n"
        "I am a Bitly link shortener bot."
        reply_to_message_id=message.id
    )

# Обработчик для сокращения ссылок
@app.on_message(filters.private & filters.regex("http|https"))
async def Bitly(client, message):
    URL = message.text
    print(f"Received URL: {URL}")  # Отладочное сообщение

    if not URL:
        await message.reply_text("Error: The URL is empty.", reply_to_message_id=message.id)
        return

    DOMAIN = "bit.ly"
    value = {'long_url': URL, 'domain': DOMAIN}
    data = json.dumps(value)
    print(f"Sending data to Bitly: {data}")  # Отладочное сообщение

    try:
        r = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, data=data)
        result = r.json()
        print(f"Bitly response: {result}")  # Отладочное сообщение

        if r.status_code == 200 and "link" in result:
            link = result["link"]
            if link and isinstance(link, str):  # Проверка, что link не пустой и является строкой
                # Убедимся, что ссылка в правильной кодировке
                link = link.encode('utf-8').decode('utf-8')
                await message.reply_text(link, reply_to_message_id=message.id)
            else:
                await message.reply_text("Error: The shortened link is empty or invalid.", reply_to_message_id=message.id)
        else:
            error_message = result.get("message", "Unknown error from Bitly.")
            await message.reply_text(f"Bitly Error: {error_message}", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Exception: {e}")  # Отладочное сообщение
        await message.reply_text(f"Error: {e}", reply_to_message_id=message.id)

# Запуск бота
app.run()