from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Узнать свое состояние'),
         KeyboardButton(text='О нас')]
    ],
    resize_keyboard=True
)

illnesses_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
                     [InlineKeyboardButton(text="Сахарный диабет", callback_data="sugar_diabet")],
                     [InlineKeyboardButton(text="Хроническая болезнь почек", callback_data="pochki")],
                     [InlineKeyboardButton(text="Ишемическая болезнь сердца", callback_data="serdce")],
                     [InlineKeyboardButton(text="Нет болезней", callback_data="nothing")],
                     # [InlineKeyboardButton(text="Выход", callback_data="exit")],
    ])

about_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='наша группа в вк',
                                                                        url='https://vk.ru/nebolej74')]])
