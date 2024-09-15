from flask import Flask, request
from aiogram import Bot, Dispatcher
import asyncio
import requests
from handlers import router

TOKEN = Bot(token='7530313667:AAG-kqhEUNv0qi3N5s8ARA8Gn1XpxyVpOwU')

async def main():
    app = Flask(__name__)
    bot = Bot(token='7530313667:AAG-kqhEUNv0qi3N5s8ARA8Gn1XpxyVpOwU')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
    app.run(host='149.154.167.40', port=443)


def webhook():
    data = request.get_json()

    if 'message' in data:
        message_text = data['message']['text']
        chat_id = data['message']['chat']['id']
        # Отправка ответа в Telegram
        response = requests.post(
            f'https://api.telegram.org/bot{TOKEN}/sendMessage',
            json={'chat_id': chat_id, 'text': f'Вы написали: {message_text}'}
        )
        return 'OK', 200

    return 'OK', 200


if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot deactivated")
