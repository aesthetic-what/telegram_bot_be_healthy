import asyncio
from flask import Flask
from aiogram import Bot, Dispatcher

from handlers import router


async def main():
    bot = Bot(token='7317856959:AAGRW7wgzy-_IAZYAQrUA57LVhujcrCnUv8')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    try:
        asyncio.run(main())
        app.run(debug=True, port=0000)
    except KeyboardInterrupt:
        print("bot deactivated")
