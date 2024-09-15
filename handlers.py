import time
from aiogram import F, Router, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboard as kb

router = Router()
# user_choices = {}  # Словарь для хранения выборов пользователей


class Health(StatesGroup):
    name = State()
    age = State()
    blood_pressure1 = State()
    blood_pressure2 = State()
    illnesses = State()
    symptoms = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'привет, я бот-помощник, группы "Челябинск, не болей!'
                         'можете ознакомится с видео-инструкцией как нужно замерять давление: '
                         'https://vk.ru/video/@0chereshnya0?section=upload&z=video432562512_456239749',
                         reply_markup=kb.main)


@router.message(F.text == 'Узнать свое состояние')
async def health(message: Message, state: FSMContext):
    await state.set_state(Health.name)
    await message.answer("Введите свое имя")


@router.message(F.text == "О нас")
async def about(message: Message):
    await message.answer("Официальная страница Центра общественного здоровья и медицинской профилактики города "
                         "Челябинска. "
                         "Мы рассказываем все, что нужно знать для вашего здоровья и вашей семьи:\n"
                         "️▪ анонсируем профилактические и спортивные мероприятия в городе;\n"
                         "️▪ говорим полезные для здоровья советы;\n "
                         "▪ даем консультации и рекомендации врачей города;\n "
                         "▪ пишем рецепты правильного питания от специалистов;\n "
                         "▪ объясняем медицинские термины.?", reply_markup=kb.about_btn)


@router.message(Health.name)
async def health_name(message: Message, state: FSMContext):
    if message.text.isdigit():
        print(message.text)
        await message.answer('Проверьте, правильно ли вы ввели свое имя')
        return

    await state.update_data(name=message.text)
    await state.set_state(Health.age)
    await message.answer('Введите свой возраст')


@router.message(Health.age)
async def health_name(message: Message, state: FSMContext):
    print(message.text)
    try:
        age = int(message.text)
        if age <= 0 or age >= 120:
            raise ValueError
        if isinstance(age, str):
            raise TypeError
    except ValueError:
        await message.answer("Возраст должен быть больше 0 и меньше 120")
        return
    except TypeError:
        await message.answer("Проверьте корректность ввода своего возраста ")
        return

    await state.update_data(age=message.text)
    await state.set_state(Health.blood_pressure1)
    await message.answer('Введите свое систолическое артериальное давление')


@router.message(Health.blood_pressure1)
async def health_name(message: Message, state: FSMContext):
    print(message.text)
    try:
        print(type(message.text))
        if int(message.text) < 100:
            raise ValueError

        if len(message.text) > 3 or len(message.text.split()) == 2 or int(message.text) >= 280:
            raise TypeError
    except ValueError:
        await message.answer("Давление не может быть меньше 100")
        return
    except TypeError:
        await message.answer("Давление введено не верно")
        return

    await state.update_data(blood_pressure1=message.text)
    await state.set_state(Health.blood_pressure2)
    await message.answer('Введите свое диастолическое артериальное давление')


@router.message(Health.blood_pressure2)
async def health_pressure2(message: Message, state: FSMContext):
    print(message.text)
    try:
        if int(message.text) < 40:
            raise ValueError

        if len(message.text.split()) == 2 or int(message.text) >= 150:
            raise TypeError

    except ValueError:
        await message.answer("Давление не может быть меньше 40")
        return
    except TypeError:
        await message.answer("Давление введено не верно")
        return

    await state.update_data(blood_pressure2=message.text)
    data = await state.get_data()
    await message.answer("выберите болезни, если таковые есть:", reply_markup=kb.illnesses_keyboard)

    sys_pressure = int(data["blood_pressure1"])
    dia_pressure = int(data["blood_pressure2"])

    bp_category = categorize_blood_pressure(sys_pressure, dia_pressure)

    # Если категория "АГ 3-й степени", сразу выводим результат и завершаем процесс
    if bp_category == "АГ 3-й степени":
        await message.answer(
            "У вас обнаружена АГ 3-й степени. "
            "Сопровождается ли повышение давления головной болью, головокружением, потемнением в глазах, "
            "мельканием мушек, загрудинной болью или отсутствием мочи? (Да/Нет)")

        await state.set_state(Health.symptoms)
        return


@router.message(Health.blood_pressure2)
async def handle_ag_3_degree(message: Message, data: dict) -> str:
    # Извлекаем нужные данные
    symptoms = data.get("symptoms", False)
    name = data["name"]
    age = data["age"]
    sys_pressure = data["blood_pressure1"]
    dia_pressure = data["blood_pressure2"]
    # Формируем сообщение в зависимости от наличия симптомов
    if symptoms:
        conclusion = "У вас АГ 3-й степени с опасными симптомами. Необходим вызов скорой медицинской помощи (112, 103)."
    else:
        conclusion = ("У вас АГ 3-й степени без опасных симптомов. "
                      "Требуется немедленная коррекция лечения, обратитесь к врачу.")

    # Возвращаем итоговое заключение
    return (f"Имя: {name}\nВозраст: {age}\n"
            f"Ваше давление: {sys_pressure}/{dia_pressure}\n"
            f"Заключение:\n{conclusion}")


@router.message(Health.symptoms)
async def health_symptoms(message: Message, state: FSMContext):
    # Получаем ответ пользователя о наличии симптомов
    print(message.text)
    symptoms = message.text.lower() == "да"

    # Сохраняем данные о симптомах в состояние FSM
    await state.update_data(symptoms=symptoms)

    # Получаем все данные о пользователе для формирования итогового вывода
    data = await state.get_data()

    # Обрабатываем данные и выводим итоговый результат с учетом симптомов
    health_status = await handle_ag_3_degree(message, data)
    await message.answer(health_status, reply_markup=kb.main)

    # Очищаем состояние после вывода данных
    await state.clear()


@router.callback_query(lambda call: call.data in ["sugar_diabet", "pochki", "serdce", "nothing"])
async def illnesses(call: types.CallbackQuery, state: FSMContext):
    # Словарь для преобразования callback_data в текст
    illnesses_dict = {
        "AG": "Артериальная гипертензия",
        "sugar_diabet": "Сахарный диабет",
        "pochki": "Хроническая болезнь почек",
        "serdce": "Ишемическая болезнь сердца",
        "nothing": "Нет болезней"
    }

    # получаем выбранную болезнь
    selected_illnesses = illnesses_dict[call.data]

    # Обновляем состояние пользователя
    await state.update_data(illnesses=selected_illnesses)
    data = await state.get_data()

    # создаем визуально ожидание
    wait = await call.message.answer('Обрабатываю вашу информацию⌛')
    time.sleep(5)
    wait2 = await call.message.answer("Еще совсем немного")
    time.sleep(5)
    await wait.delete()
    await wait2.delete()

    health_status = await check_ur_health(call, state)
    await call.message.answer(f'Ваше имя: {data["name"]}\nВаш возраст: {data["age"]}\n'
                              f'Ваше давление: {data["blood_pressure1"]}/{data["blood_pressure2"]}'
                              f'\nВаша болезнь: {data["illnesses"]}\n'
                              f'Заключение:\n{health_status}', reply_markup=kb.main)
    await state.clear()


# @router.callback_query(lambda call: call.data in ["sugar_diabet", "pochki", "serdce", "nothing"])
# async def handle_illness_selection(query: types.CallbackQuery, state: FSMContext):
#     user_id = query.from_user.id
#     selected_illness = query.data
#     print(user_choices)
#     print(user_id)
#     print(selected_illness)
#
#     if user_id not in user_choices:
#         user_choices[user_id] = set()
#
#     if selected_illness in user_choices[user_id]:
#         user_choices[user_id].remove(selected_illness)
#     else:
#         user_choices[user_id].add(selected_illness)
#
#     # Сохраняем выбранные болезни в состоянии
#     await state.update_data(illnesses=user_choices[user_id])
#
#     updated_keyboard = update_keyboard_text(kb.illnesses_keyboard, user_choices[user_id])
#
#     await query.message.edit_text(
#         'Выберите болезни из списка (можете выбрать несколько):',
#         reply_markup=updated_keyboard)
#     await query.answer()
#
#     # Обновляем клавиатуру в сообщении
#     await query.message.edit_reply_markup(reply_markup=updated_keyboard)


# def update_keyboard_text(keyboard, selected_options):
#     """Обновляет текст кнопок клавиатуры, добавляя "✅" к выбранным опциям."""
#     for row in keyboard.inline_keyboard:
#         for button in row:
#             if button.callback_data in selected_options:
#                 if '✅' not in button.text:
#                     button.text = button.text + ' ✅'
#             else:
#                 button.text = button.text.replace(' ✅', '')
#     return keyboard


# @router.callback_query(F.data == "exit")
# async def exit_illness_selection(call: types.CallbackQuery, state: FSMContext):
#     user_id = call.from_user.id
#     data = await state.get_data()
#
#     # Используем user_choices[user_id] для получения выбранных болезней
#     selected_illnesses = ", ".join(user_choices.get(user_id, [])) or "Нет болезней"
#
#     health_status = await check_ur_health(call, state)  # Передаем call вместо message
#     await call.message.answer(
#         f'Ваше имя: {data["name"]}\n'
#         f'Ваш возраст: {data["age"]}\n'
#         f'Ваше давление: {data["blood_pressure1"]}/{data["blood_pressure2"]}\n'
#         f'Ваши болезни: {selected_illnesses}\n'
#         f'Заключение:\n{health_status}',
#         reply_markup=kb.main
#     )
#     await state.clear()
#     await call.message.delete()  # Удаляем сообщение с выбором болезней


def categorize_blood_pressure(sys_pressure: int, dia_pressure: int) -> str:
    # Определяем категорию на основании наибольшего давления
    if sys_pressure >= 180 or dia_pressure >= 110:
        return "АГ 3-й степени"
    elif 160 <= sys_pressure or 100 <= dia_pressure:
        return "АГ 2-й степени, требуется коррекция лечения, обратитесь к лечащему врачу"
    elif 140 <= sys_pressure or 90 <= dia_pressure:
        return "АГ 1-й степени, требуется коррекция лечения, обратитесь к лечащему врачу"
    elif sys_pressure >= 140 and dia_pressure < 90:
        return "Изолированная систолическая гипертензия"
    elif sys_pressure < 120 and dia_pressure < 80:
        return "Оптимальное"
    elif 120 <= sys_pressure <= 129 and dia_pressure < 85:
        return "Нормальное"
    elif 130 <= sys_pressure or 85 <= dia_pressure:
        return "Высокое нормальное"
    else:
        return "Неопределенная категория"


def get_blood_pressure_advice(category: str) -> str:
    advice = {
        "Оптимальное": "Ваше давление в оптимальном диапазоне. Продолжайте вести здоровый образ жизни.",
        "Нормальное": "Ваше давление в нормальном диапазоне. Поддерживайте здоровый образ жизни.",
        "Высокое нормальное": "Ваше давление немного повышено. "
                              "Рекомендуется обратить внимание на диету и физическую активность.",
        "АГ 1-й степени": "У вас артериальная гипертензия. "
                          "Рекомендуется консультация с врачом для разработки плана лечения.",
        "АГ 2-й степени": "У вас артериальная гипертензия. "
                          "Необходима срочная консультация с врачом и, вероятно, медикаментозное лечение.",
        "АГ 3-й степени": "У вас артериальная гипертензия 3-й степени. "
                          "Требуется немедленная медицинская помощь и интенсивное лечение.",
        "Изолированная систолическая гипертензия": "У вас изолированная систолическая гипертензия. Необходима "
                                                   "консультация с кардиологом для дальнейшего обследования и лечения.",
        "Неопределенная категория": "Ваши показатели давления не попадают в стандартные категории. "
                                    "Рекомендуется дополнительное обследование у врача."
    }
    return advice.get(category, "Рекомендуется консультация с врачом для оценки вашего состояния.")


def check_blood_pressure(age: int, sys_pressure: int, dia_pressure: int):
    category = categorize_blood_pressure(sys_pressure, dia_pressure)

    if 18 <= age <= 64:
        sys_target = "130"
        dia_target = "70-79"
    elif 65 <= age <= 79:
        sys_target = "130-139"
        dia_target = "70-79"
    else:  # age >= 80
        sys_target = "130-139"
        dia_target = "70-79"

    if category in ["Оптимальное", "Нормальное"]:
        return f"Ваше давление в норме ({category})."
    elif category == "Высокое нормальное":
        return f"Ваше давление немного повышено ({category})."
    elif sys_pressure > int(sys_target.split('-')[-1]) or dia_pressure > int(dia_target.split('-')[-1]):
        return f"Давление выше целевого значения. Целевое: {sys_target}/{dia_target}."
    elif sys_pressure < int(sys_target.split('-')[0].replace('≤', '')) or dia_pressure < int(dia_target.split('-')[0]):
        return (f"Давление ниже целевого значения. Целевое: {sys_target}/{dia_target}. Рекомендуется "
                f"консультация с врачом.")
    else:
        return f"Давление в пределах целевого значения: {sys_target}/{dia_target}."


async def process_symptoms(message: Message) -> str:
    symptoms = message.text.lower() == "да"
    if symptoms:
        return "У вас АГ 3-й степени с опасными симптомами. Необходим вызов СМП 112, 103"
    else:
        return "У вас АГ 3-й степени без опасных симптомов. Необходима коррекция терапии, обратитесь к лечащему врачу"


@router.callback_query(Health.illnesses, lambda call: call.data in ["AG", "sugar_diabet", "pochki", "serdce",
                                                                    "ataka", "nothing"])
async def check_ur_health(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    age = int(data["age"])
    sys_pressure = int(data["blood_pressure1"])
    dia_pressure = int(data["blood_pressure2"])
    bp_category = categorize_blood_pressure(sys_pressure, dia_pressure)
    illnesses_dict = {
        "AG": "Артериальная гипертензия",
        "sugar_diabet": "Сахарный диабет",
        "pochki": "Хроническая болезнь почек",
        "serdce": "Ишемическая болезнь сердца",
        "nothing": "Нет болезней"
    }
    symptoms = data.get("symptoms", False)

    selected_ill = illnesses_dict[call.data].lower()
    print(selected_ill)

    # Мгновенная проверка для АГ 3-й степени
    if bp_category == "АГ 3-й степени":
        if symptoms:
            bp_status = "У вас АГ 3-й степени с опасными симптомами. Необходим вызов СМП 112, 103"
        else:
            bp_status = ("У вас АГ 3-й степени без опасных симптомов. Необходима коррекция терапии, "
                         "обратитесь к лечащему врачу")
        return bp_status

    bp_status = check_blood_pressure(age, sys_pressure, dia_pressure)

    # Обновленное уведомление для болезней высокого риска
    high_risk_illnesses = ["артериальная гипертензия", "сахарный диабет", "хроническая болезнь почек",
                           "иемическая болезнь сердца"]
    if selected_ill in high_risk_illnesses:
        illness_status = (f"У вас {selected_ill}. Это заболевание связано с высоким риском осложнений, "
                          f"обратитесь к врачу для срочной консультации.")
    elif selected_ill == "нет болезней":
        illness_status = "У вас нет указанных заболеваний."
    else:
        illness_status = "Ваше заболевание не указано в списке высокого риска."

    age_advice = ""
    if age < 18:
        age_advice = ("Ваш возраст меньше 18 лет. Нормы давления могут отличаться, "
                      "рекомендуется консультация с педиатром.")
    elif age > 65:
        age_advice = "В вашем возрасте особенно важно регулярно контролировать давление и консультироваться с врачом."

    return (f"Категория вашего артериального давления: {bp_category}\n"
            f"{bp_status}\n"
            f"{age_advice}\n"
            f"{illness_status}\n"
            f"Рекомендуется регулярно контролировать свое здоровье.")
