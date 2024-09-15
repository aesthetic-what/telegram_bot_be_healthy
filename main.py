from fastapi import FastAPI, Request
import uvicorn
from aiogram import Bot, Dispatcher
import asyncio
import requests
from handlers import router

TOKEN = Bot(token='7530313667:AAG-kqhEUNv0qi3N5s8ARA8Gn1XpxyVpOwU')

async def main():
    app = FastAPI()
    bot = Bot(token='7530313667:AAG-kqhEUNv0qi3N5s8ARA8Gn1XpxyVpOwU')
    dp = Dispatcher()
    dp.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    await dp.start_polling(bot) 


# Функция для обработки webhook запросов
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if "message" in data:
        message_text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        await bot.send_message(chat_id=chat_id, text=f"Вы написали: {message_text}")
    return "OK"


if __name__ == '__main__':
    executor.start_webhook(dispatcher=dp, webhook_path="/",
                          on_startup=bot.set_webhook, 
                          on_shutdown=bot.delete_webhook,
                          skip_updates=True, 
                          host="0.0.0.0", port=8000, url_path='/webhook')
