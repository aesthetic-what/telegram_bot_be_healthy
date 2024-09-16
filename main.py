import asyncio
import requests
from handlers import router
from aiogram import Bot, Dispatcher


async def main():
    bot = Bot(token='7530313667:AAG-kqhEUNv0qi3N5s8ARA8Gn1XpxyVpOwU')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot) 



if __name__ == '__main__':
    try:
        # Запуск основного цикла бота
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
