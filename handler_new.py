from aiogram import F, Router, types, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboard as kb

router = Router()

bot = Bot(token='7530313667:AAG-kqhEUNv0qi3N5s8ARA8Gn1XpxyVpOwU')


class Health(StatesGroup):
    name = State()
    age = State()
    blood_pressure1 = State()
    blood_pressure2 = State()
    illnesses = State()
    symptoms = State()


# Шаблон для сообщений о давлении
def generate_health_message(data):
    return (f"Ваше имя: {data['name']}\nВаш возраст: {data['age']}\n"
            f"Ваше давление: {data['blood_pressure1']}/{data['blood_pressure2']}")


# Категоризация давления и рекомендации
def categorize_blood_pressure(sys_pressure, dia_pressure):
    if sys_pressure >= 180 or dia_pressure >= 110:
        category = "АГ 3-й степени"
        recommendations = (
            "Ваш уровень артериального давления (АД) значительно выше целевых значений. "
            "Необходимо незамедлительно обратиться к врачу для коррекции лечения и консультации. "
            "Рекомендуется также регулярно контролировать АД утром и вечером."
        )

    elif sys_pressure >= 160 or dia_pressure >= 100:
        category = "Артериальная гипертензия"
        recommendations = (
            "Ваш уровень артериального давления выше нормы. Рекомендуется консультация с врачом для оценки состояния "
            "и, возможно, корректировка лечения. Также ведите дневник АД и частоты сердечных сокращений."
        )

    elif sys_pressure >= 140 or dia_pressure >= 90:
        category = "Артериальная гипертензия"
        recommendations = (
            "Ваш уровень артериального давления выше нормы. Рекомендуем регулярно измерять давление "
            "и обратиться к лечащему врачу для консультации. Требуется коррекция лечения."
        )

    elif 120 <= sys_pressure <= 139 or 80 <= dia_pressure < 89:
        category = "Нормальное давление"
        recommendations = (
            "Ваше давление находится в пределах нормальных значений, но немного выше оптимальных. "
            "Поддерживайте здоровый образ жизни для сохранения или улучшения показателей.")

    else:
        category = "Оптимальное давление"
        recommendations = (
            "Ваше давление находится в оптимальных пределах. "
            "Продолжайте следить за своим здоровьем и ведите активный образ жизни."
        )
    return category, recommendations


# Функция для обработки возраста
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if not (0 < age < 120):
            raise ValueError
    except ValueError:
        await message.answer("Возраст должен быть между 1 и 120 годами.")
        return
    await state.update_data(age=age)
    await state.set_state(Health.blood_pressure1)
    await message.answer("Введите ваше систолическое (верхнее) давление")


async def check_blood_pressure(age: int, sys_pressure: int, dia_pressure: int):                                   # проверка уровня давления
    # Определяем целевые значения в зависимости от возраста
    if 18 <= age <= 64:
        sys_target_min = 120  # Нижний предел для систолического давления, для "≤130"
        sys_target_max = 139  # Верхний предел
        dia_target_min = 70  # Нижний предел для диастолического
        dia_target_max = 89  # Верхний предел
    elif 65 <= age <= 79:
        sys_target_min = 130
        sys_target_max = 139
        dia_target_min = 70
        dia_target_max = 79
    else:  # age >= 80
        sys_target_min = 130
        sys_target_max = 139
        dia_target_min = 70
        dia_target_max = 79

    # Проверяем категорию давления
    category = categorize_blood_pressure(sys_pressure, dia_pressure)

    # Выводим рекомендации в зависимости от категории давления
    if category in ["Оптимальное", "Нормальное", "Высокое нормальное"]:
        return f"Ваше давление в норме ({category})."

    # Проверяем, если давление выше Рекомендуемого значения
    if sys_pressure > sys_target_max or dia_pressure > dia_target_max:
        return (
            f"Давление выше рекомендуемого значения. Рекомендуемое: {sys_target_min}-{sys_target_max}/{dia_target_min}-{dia_target_max}.")
    # Проверяем, если давление ниже Рекомендуемого значения
    elif sys_pressure < sys_target_min or dia_pressure < dia_target_min:
        return (
            f"Давление ниже рекомендуемого. Рекомендуемое: {sys_target_min}-{sys_target_max}/{dia_target_min}-{dia_target_max}. "
            f"Рекомендуется консультация с врачом.")
    # Если давление в пределах нормы
    else:
        return (f"Давление в пределах Рекомендуемого значения: {sys_target_min}-{sys_target_max}/{dia_target_min}-"
                f"{dia_target_max}.")


# Функция для обработки давления
async def process_blood_pressure(message: Message, state: FSMContext, pressure_type: str):
    try:
        pressure = int(message.text)
        if pressure_type == "blood_pressure1" and pressure < 100:
            raise ValueError("Систолическое давление не может быть меньше 100")
        if pressure_type == "blood_pressure2" and pressure < 50:
            raise ValueError("Диастолическое давление не может быть меньше 50")
    except ValueError as e:
        await message.answer(str(e))
        return
    await state.update_data({pressure_type: pressure})
    next_state = Health.blood_pressure2 if pressure_type == "blood_pressure1" else Health.illnesses
    await state.set_state(next_state)
    if pressure_type == "blood_pressure1":
        await message.answer("Введите ваше диастолическое (нижнее) давление")
    else:
        data = await state.get_data()
        category = categorize_blood_pressure(data["blood_pressure1"], data["blood_pressure2"])
        if category == "АГ 3-й степени":
            await message.answer("Есть ли у вас симптомы, такие как головная боль, головокружение? (Да/Нет)")
            await state.set_state(Health.symptoms)
        else:
            await message.answer("Были ли у вас диагностированы болезни?", reply_markup=kb.illnesses_keyboard)


user_choices = {}


# Обработчик для callback'ов
@router.callback_query(lambda call: call.data)
async def process_callback(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    # Проверяем если выбрали артериальную гипертензию
    if call.data == "AG":
        # Сохраняем выбор пользователя
        user_choices[user_id] = ["Артериальная гипертензия"]

        await bot.send_message(user_id, "Вы выбрали Артериальную гипертензию. "
                                        "Выберите дополнительное заболевание:", reply_markup=kb.cont_ill_keyboard)
    else:
        # Если выбрана любая другая болезнь, добавляем ее в список пользователя
        if user_id in user_choices:
            user_choices[user_id].append(call.data)
        else:
            user_choices[user_id] = [call.data]

        # Если выбран "Нет болезней", прекращаем выбор и выводим результат
        if call.data == "nothing":
            await generate_final_message(user_id)
            # Очищаем данные пользователя после завершения
            user_choices.pop(user_id, None)
        else:
            await bot.send_message(user_id, "Вы выбрали: " + call.data)

    # Не забудьте ответить на callback, чтобы кнопка не оставалась подвешенной
    await bot.answer_callback_query(call.id)


# Генерация итогового сообщения
async def generate_final_message(user_id):
    diseases = user_choices.get(user_id, [])

    if diseases:
        # Генерируем текст с перечислением выбранных болезней
        result_message = "Вы выбрали следующие заболевания: \n" + "\n".join(diseases)
    else:
        result_message = "Вы не выбрали никаких заболеваний."

    # Отправляем итоговое сообщение пользователю
    await bot.send_message(user_id, result_message)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Видео-инструкция как измерять давление: '
                         'https://vk.ru/video/@0chereshnya0?section=upload&z=video432562512_456239749',
                         reply_markup=kb.main)


@router.message(F.text == "Оценить уровень артериального давления")
async def health_start(message: Message, state: FSMContext):
    await state.set_state(Health.name)
    await message.answer("Введите ваше имя")


@router.message(Health.name)
async def health_name(message: Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer("Имя не может содержать цифры.")
        return
    await state.update_data(name=message.text)
    await state.set_state(Health.age)
    await message.answer("Введите ваш возраст")


@router.message(Health.age)
async def health_age(message: Message, state: FSMContext):
    await process_age(message, state)


@router.message(Health.blood_pressure1)
async def health_pressure1(message: Message, state: FSMContext):
    await process_blood_pressure(message, state, "blood_pressure1")


@router.message(Health.blood_pressure2)
async def health_pressure2(message: Message, state: FSMContext):
    await process_blood_pressure(message, state, "blood_pressure2")


@router.message(Health.symptoms)
async def health_symptoms(message: Message, state: FSMContext):
    symptoms = message.text.lower() == "да"
    await state.update_data(symptoms=symptoms)
    data = await state.get_data()
    category = categorize_blood_pressure(data["blood_pressure1"], data["blood_pressure2"])
    message_text = f"{generate_health_message(data)}\nВаш диагноз: {category}\n"
    message_text += "Требуется медицинская помощь!" if symptoms else "Обратитесь к врачу."
    await message.answer(message_text, reply_markup=kb.SMD)
    await state.clear()


@router.callback_query(lambda call: call.data in ["AG", "CHD", "CKD", "serdce", "insult", "nothing"])
async def handle_illness(call: types.CallbackQuery, state: FSMContext):
    illnesses_dict = {
        "AG": "Артериальная гипертензия",
        "CHD": "Сахарный диабет",
        "CKD": "Хроническая болезнь почек",
        "serdce": "Ишемическая болезнь сердца",
        "insult": "Инсульт",
        "nothing": "Нет болезней"
    }
    selected_illness = illnesses_dict[call.data]
    await state.update_data(illness=selected_illness)
    data = await state.get_data()
    await call.message.answer(f"{generate_health_message(data)}\nЗаключение: {selected_illness}",
                              reply_markup=kb.SMD)
    await state.clear()


@router.callback_query(lambda call: call.data in ["yes", "no"])
async def doctor_appointment(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        await call.message.answer("Вот список поликлиник для записи: ...", reply_markup=kb.SMD)
    else:
        await call.message.answer("Регулярное повышение давления опасно для здоровья.")
    await state.clear()


@router.callback_query(lambda call: call.data["AG", "CHD", "CKD", "serdce", "insult", "nothing"])
# Функция для генерации и вывода итогового сообщения о здоровье
async def output_final_health_results(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    age = int(data["age"])
    sys_pressure = int(data["blood_pressure1"])
    dia_pressure = int(data["blood_pressure2"])

    # Категоризация давления
    bp_category, bp_recommendations = categorize_blood_pressure(sys_pressure, dia_pressure)

    # Определение целевых показателей для давления
    bp_check_result = check_blood_pressure(age, sys_pressure, dia_pressure)

    # Получение информации о выбранной болезни
    selected_illness = data.get("illness", "Нет болезней")

    # Рекомендации по возрасту
    age_advice = ""
    if age < 18:
        age_advice = ("Этот бот предназначен для лиц старше 18 лет. Если у вас есть жалобы, "
                      "пожалуйста, обратитесь к педиатру.")
    elif age > 65:
        age_advice = ("В вашем возрасте особенно важно контролировать давление и регулярно "
                      "консультироваться с врачом для предупреждения осложнений.")

    # Основные рекомендации в зависимости от давления
    if bp_category == "Нормальное" or bp_category == "Оптимальное":
        general_recommendations = ("Ваш уровень артериального давления находится в пределах нормы. "
                                   "Продолжайте вести здоровый образ жизни и следите за давлением.")
    else:
        general_recommendations = ("Ваш уровень артериального давления выше целевых значений. "
                                   "Регулярно измеряйте давление утром и вечером, ведите дневник АД и "
                                   "обратитесь к врачу для корректировки лечения.")

    # Специфические рекомендации на основе выбранных болезней
    illness_advice = ""
    if selected_illness == "Сахарный диабет":
        illness_advice = ("При наличии сахарного диабета важно особенно тщательно контролировать артериальное "
                          "давление и уровень сахара в крови. Следуйте рекомендациям врача.")
    elif selected_illness == "Хроническая болезнь почек":
        illness_advice = ("При хронических заболеваниях почек важно поддерживать давление на низком уровне для "
                          "предотвращения дальнейшего ухудшения функции почек.")
    elif selected_illness == "Ишемическая болезнь сердца":
        illness_advice = ("При ишемической болезни сердца важно контролировать уровень давления и холестерина, "
                          "чтобы снизить риск сердечных осложнений.")
    elif selected_illness == "Артериальная гипертензия":
        illness_advice = ("Для контроля артериальной гипертензии необходима регулярная проверка давления и прием "
                          "назначенных препаратов. Проконсультируйтесь с врачом для корректировки лечения.")
    else:
        illness_advice = "У вас нет заболеваний, требующих дополнительных рекомендаций."

    # Формирование финального сообщения
    final_message = (f"Рекомендуемый уровень артериального давления для Вас: {bp_category}\n"
                     f"{bp_check_result}\n"
                     f"{bp_recommendations}\n"
                     f"{age_advice}\n"
                     f"{general_recommendations}\n"
                     f"{illness_advice}")

    # Отправка сообщения пользователю
    await bot.send_message(call.from_user.id, final_message)