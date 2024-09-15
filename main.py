from flask import Flask, request
from aiogram import Bot, Dispatcher
import asyncio
import requests
from handlers import router

TOKEN = Bot(token='7530313667:AAFQz08Gnrv-Mqty2IA1cT1COzXqgYo84I8')

async def main():
    bot = Bot(token='7530313667:AAFQz08Gnrv-Mqty2IA1cT1COzXqgYo84I8')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


app = Flask(__name__)


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
        asyncio.run(main())
        app.run(host='0.0.0.0', port=90)
    except KeyboardInterrupt:
        print("bot deactivated")
