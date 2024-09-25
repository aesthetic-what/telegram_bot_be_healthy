import os

from aiogram import F, Router, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboard as kb

router = Router()


class Health(StatesGroup):
    name = State()
    age = State()
    blood_pressure1 = State()
    blood_pressure2 = State()
    has_ag = State()
    illnesses = State()
    symptoms = State()


# Создаем словарь для болезней: ключ — аббревиатура, значение — полное название болезни
ILLNESSES_DICT = {
    'insult': 'Инсульт',
    'diabetes': 'Сахарный диабет',
    'CHD': 'Ишемическая болезнь сердца',
    'CKD': 'Хроническая болезнь почек'
}

USERS_FILE = "users.txt"


# Функция для проверки нового пользователя и обновления количества пользователей
def is_new_user(user_tag: str) -> bool:
    # Проверяем, существует ли файл с пользователями
    if not os.path.exists(USERS_FILE):
        # Если файла нет, создаем его и записываем текущего пользователя
        with open(USERS_FILE, 'w') as f:
            f.write("1\n")  # Первая строка — количество пользователей
            f.write(f"{user_tag}\n")  # Вторая строка — первый пользователь
        return True

    # Если файл существует, читаем его содержимое
    with open(USERS_FILE, 'r') as f:
        lines = f.read().splitlines()

    # Первая строка — это количество пользователей, остальные — теги пользователей
    count = int(lines[0])
    users = lines[1:]

    # Если пользователь уже в списке, возвращаем False
    if user_tag in users:
        return False

    # Если пользователя нет в списке, добавляем его и увеличиваем счетчик
    with open(USERS_FILE, 'w') as f:
        f.write(f"{count + 1}\n")  # Обновляем количество пользователей
        for user in users:
            f.write(f"{user}\n")  # Перезаписываем старые теги
        f.write(f"{user_tag}\n")  # Добавляем нового пользователя

    return True


@router.message(CommandStart())
async def cmd_start(message: Message):
    # Получаем уникальный user_id пользователя или его username
    user_id = str(message.from_user.id)  # Можно использовать message.from_user.username

    # Проверяем, новый ли это пользователь
    if is_new_user(user_id):
        await message.answer('Можете ознакомится с видео-инструкцией как нужно измерять давление: '
                             'https://vk.ru/video/@0chereshnya0?section=upload&z=video432562512_456239749',
                             reply_markup=kb.main)
    else:
        await message.answer('Можете ознакомится с видео-инструкцией как нужно измерять давление: '
                             'https://vk.ru/video/@0chereshnya0?section=upload&z=video432562512_456239749',
                             reply_markup=kb.main)


@router.message(F.text == 'Оценить уровень артериального давления')
async def health(message: Message, state: FSMContext):
    await state.set_state(Health.name)
    await message.answer("Укажите свое имя")


@router.message(F.text == "О нас")
async def about(message: Message):
    await message.answer("Официальная страница Центра общественного здоровья и медицинской профилактики города "
                         "Челябинска. "
                         "Мы рассказываем все, что нужно знать для вашего здоровья и вашей семьи:\n"
                         "️▪ анонсируем профилактические и спортивные мероприятия в городе;\n"
                         "️▪ говорим полезные для здоровья советы;\n "
                         "▪ даем консультации и рекомендации врачей города;\n "
                         "▪ пишем рецепты правильного питания от специалистов;\n "
                         "▪ объясняем медицинские термины.", reply_markup=kb.about_btn)


@router.message(Health.name)
async def health_name(message: Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer('Проверьте, правильно ли вы ввели свое имя')
        return
    await state.update_data(name=message.text)
    await state.set_state(Health.age)
    await message.answer('Введите свой возраст')


@router.message(Health.age)
async def health_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0 or age >= 120:
            raise ValueError
        if message.text < '18':
            await message.answer(
                "Данный бот предназначен для лиц старше 18 лет. Если у вас есть проблемы, то обратитесь "
                "к вашему лечащему педиатру", reply_markup=kb.main)
            await state.clear()
            return
    except ValueError:
        await message.answer("Возраст должен быть больше 0 и меньше 120")
        return

    await state.update_data(age=age)
    await state.set_state(Health.blood_pressure1)
    await message.answer('Ваше систолическое (верхнее) давление')


def check_hypertension(bp1: int, bp2: int) -> bool:
    # Check if the systolic or diastolic values fall within the range for grades 2 and 3 combined
    return (160 <= bp1 <= 180) or (100 <= bp2 <= 110)


@router.message(Health.blood_pressure1)
async def health_pressure1(message: Message, state: FSMContext):
    try:
        pressure = int(message.text)
        if pressure < 60 or pressure >= 280:
            raise ValueError
    except ValueError:
        await message.answer("Давление должно быть в диапазоне от 60 до 280")
        return

    bp1 = int(message.text)
    await state.update_data(blood_pressure1=bp1)

    await state.update_data(blood_pressure1=pressure)
    await state.set_state(Health.blood_pressure2)
    await message.answer('Ваше диастолическое (нижнее) давление')


@router.message(Health.blood_pressure2)
async def health_pressure2(message: Message, state: FSMContext):
    try:
        pressure = int(message.text)
        if pressure < 50 or pressure >= 150:
            raise ValueError
    except ValueError:
        await message.answer("Давление должно быть в диапазоне от 50 до 150")
        return

    bp2 = int(message.text)
    await state.update_data(blood_pressure2=bp2)

    # Retrieve blood pressure values
    user_data = await state.get_data()
    bp1 = user_data.get('blood_pressure1')

    # Check for arterial hypertension grade 2 and 3 combined
    if check_hypertension(bp1, bp2):
        await state.set_state(Health.symptoms)
        await message.answer(
            "Сопровождается ли повышение давления головной болью, головокружением, потемнением в глазах, "
            "мельканием мушек, загрудинной болью или отсутствием мочи? (Да/Нет)")
        return

    await state.update_data(blood_pressure2=pressure)
    await state.set_state(Health.has_ag)
    await message.answer("Ставил ли Вам врач диагноз «Гипертоническая болезнь»?", reply_markup=kb.symptom_key)


@router.callback_query(
    lambda call: call.data in ILLNESSES_DICT.keys())
async def select_illness(call: types.CallbackQuery, state: FSMContext):
    # Получаем текущий список болезней
    data = await state.get_data()
    selected_illnesses = data.get('illnesses', [])

    # Получаем полное название болезни по аббревиатуре
    selected_illness = ILLNESSES_DICT[call.data]

    # Добавляем выбранное заболевание, если его еще нет в списке
    if selected_illness not in selected_illnesses:
        selected_illnesses.append(selected_illness)
        await state.update_data(illnesses=selected_illnesses)

    # Выводим пользователю список выбранных болезней
    await call.message.answer(f"Вы выбрали: {', '.join(selected_illnesses)}")


# Завершение выбора болезней
@router.callback_query(lambda call: call.data == "done")
async def done_selection(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_illnesses = data.get('illnesses', [])

    if not selected_illnesses:
        await call.message.answer("Вы не выбрали ни одной болезни.")
        return

    # Связываем с функцией обработки давления
    await process_results(call.message, state)


@router.message(Health.symptoms)
async def ask_symptoms(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    sys_pressure = int(data["blood_pressure1"])
    dia_pressure = int(data["blood_pressure2"])

    if message.text.lower() == "да":
        await message.answer(
            f"Имя: {name}\n"
            f"Возраст: {age}\n"
            f"Ваше артрериальное давление: {sys_pressure}/{dia_pressure}\n"
            "Ваш уровень артериального давления (АД) намного выше целевых значений. Рекомендуем Вам "
            "регулярно изменять давление утром и вечером, а также вести дневник АД и частоты сердечных "
            "сокращений.")

        await message.answer("По описанным Вами жалобам наблюдаются симптомы гипертонического криза.\nЭто тяжелое "
                             "состояние, требующее вызова скорой медицинской помощи (тел. 103, 112).")

    elif message.text.lower() == "нет":
        await message.answer("Есть ли у Вас сопутствующие заболевания из списка ниже? "
                             "(После выбора заболеваний нажмите «готово»)", reply_markup=kb.cont_ill_keyboard)
        return


@router.callback_query(Health.has_ag)
async def process_has_ag(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(has_ag=call.data == "yes_s")

    if call.data == "yes_s":
        await state.set_state(Health.illnesses)
        await call.message.answer("Есть ли у Вас сопутствующие заболевания из списка ниже? "
                                  "(После выбора заболеваний нажмите «готово»)", reply_markup=kb.cont_ill_keyboard)
    else:
        await process_results(call.message, state)


@router.callback_query(Health.illnesses)
async def process_illnesses(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(illnesses=call.data)
    await process_results(call.message, state)


async def process_results(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name', 'Пользователь')  # Добавим имя пользователя
    age = data['age']
    sys_pressure = data['blood_pressure1']
    dia_pressure = data['blood_pressure2']
    has_ag = data.get('has_ag', False)
    illnesses = data.get('illnesses', 'nothing')

    # Обработка давления
    result = check_blood_pressure(age, sys_pressure, dia_pressure, has_ag, illnesses)

    # Добавим имя, возраст и давление в сообщение
    final_message = (f"Имя: {name}\n"
                     f"Возраст: {age}\n"
                     f"Ваше артрериальное давление: {sys_pressure}/{dia_pressure}\n"
                     f"Рекомендуемая норма артериального давления для Вас: {normal_pressure(illnesses)}\n"
                     f"{result['message']}")

    print(f"{result['is_normal']}")
    if not result['is_normal']:
        print("а почему")

    if not result['is_normal']:
        print("is_normal detected")
        if has_ag:
            await message.answer(f"{final_message}\n\nХотели бы вы записаться на прием к врачу?", reply_markup=kb.SMD)
    else:
        await message.answer(final_message)

    await state.clear()


def check_blood_pressure(age: int, sys_pressure: int, dia_pressure: int, has_ag: bool, illnesses):
    # Убедимся, что illnesses является списком
    if isinstance(illnesses, str):
        illnesses = [illnesses]  # Преобразуем строку в список с одним элементом

    if has_ag:
        if any(illness in ['Сахараный диабет', 'Инсульт', 'Ишемическая болезнь сердца'] for illness in illnesses):
            if age <= 64:
                target_sys = [100, 129]
                target_dia = [60, 79]
            else:
                target_sys = [100, 139]
                target_dia = [60, 79]
        elif 'Хроническая болезнь почек' in illnesses:
            target_sys = [130, 139]
            target_dia = [70, 79]
            print("CKD detected")
        else:  # 'nothing'
            target_sys = [120, 129]
            target_dia = [70, 79]
            print("nothing")
            print(illnesses)
    else:
        target_sys = [0, 140]
        target_dia = [0, 90]

    # Логика определения состояния давления
    not_normal = sys_pressure < target_sys[0] or dia_pressure < target_dia[0]
    is_normal = target_sys[0] <= sys_pressure <= target_sys[1] and target_dia[0] <= dia_pressure <= target_dia[1]
    critical = sys_pressure < 100 or dia_pressure < 60

    # Добавим отладочные сообщения для проверки логики
    print(f"sys_pressure: {sys_pressure}, dia_pressure: {dia_pressure}")
    print(f"is_normal: {is_normal}, not_normal: {not_normal}, critical: {critical}")

    # Логика формирования сообщений
    # 1. Проверка для нормального давления у пациентов с ХБП
    if 'Хроническая болезнь почек' in illnesses and is_normal:
        message = ("Ваш уровень артериального давления в норме.\n"
                   "Рекомендуем Вам регулярно измерять давление утром и вечером, "
                   "а также вести дневник АД и частоты сердечных сокращений.")
        print("normal")

    # 2. Критическое давление
    elif critical:
        message = "Ваше давление ниже общепринятой нормы. Необходимо обратиться к врачу для определения причин."

    # 3. Давление ниже нормы
    elif not_normal:
        message = "Ваш уровень артериального давления ниже нормы. Рекомендуется обратиться к участковому терапевту."

    # 4. Повышенное давление с ХБП
    elif 'Хроническая болезнь почек' in illnesses and sys_pressure > target_sys[1] and dia_pressure > target_dia[1]:
        message = ("Ваш уровень артериального давления (АД) выше нормы.\n"
                   "Рекомендуем Вам регулярно измерять давление утром и вечером, "
                   "а также вести дневник АД и частоты сердечных сокращений.\n"
                   "Требуется назначение или коррекция лечения. "
                   "Обратитесь за консультацией к лечащему врачу.")

    # 5. Общее нормальное давление
    elif is_normal:
        message = ("Ваш уровень артериального давления в норме. "
                   "Продолжайте придерживаться принципов здорового образа жизни.\n"
                   " Если у вас есть жалобы на состояние здоровья, рекомендуем обратиться к участковому терапевту.")

    # 6. Повышенное давление
    else:
        message = ("Ваш уровень артериального давления (АД) выше нормы.\n"
                   "Рекомендуем Вам регулярно измерять давление утром и вечером, "
                   "а также вести дневник АД и частоты сердечных сокращений.\n"
                   "Требуется назначение или коррекция лечения. "
                   "Обратитесь за консультацией к лечащему врачу.")

    return {'is_normal': is_normal, 'message': message}


def normal_pressure(illnesses):

    if isinstance(illnesses, str):
        illnesses = [illnesses]

    if any(illness in ['Сахараный диабет', 'Инсульт', 'Ишемическая болезнь сердца'] for illness in illnesses):
        message = "120-129/70-79"
        print("any detected")

    elif 'Хроническая болезнь почек' in illnesses:
        message = "130-139/70-79"
        print("CKD detected")

    else:
        message = '<140/90'
        print("normal detected")
    return message


@router.callback_query(lambda call: call.data in ["yes", "no"])
async def smd(call: types.CallbackQuery):
    doctor_dict = {
        "yes": "Для записи на прием к специалисту Вы можете воспользоваться электронными сервисами или позвонить "
               "в регистратуру медицинской организации, к которой прикреплены\n"
               "- Портал Госуслуги https://gosuslugi.ru/\n"
               "- Региональный портал https://talon.zdrav74.ru/\n"
               "Контакты регистратур медицинских организаций г. Челябинск:\n"
               "ГАУЗ ОТКЗ ГКБ №1 г. Челябинск +7(351)700-24-99\n"
               "ГАУЗ ГКБ №2   +7(351)700-00-82\n"
               "ГБУЗ ГКБ № 5  +7(351)700-05-00\n"
               'ГБУЗ "ГКП №5 г. Челябинск" +7(351)700-75-82\n'
               'ГАУЗ "ГКБ №6 г. Челябинск"  +7(351)731-66-66\n'
               'ГАУЗ "ГКП №8 г. Челябинск"  +7(351)700-00-33\n'
               'ГАУЗ ОЗП ГКБ № 8 +7(351)700-10-80\n'
               'ГАУЗ "ГКБ № 9 г. Челябинск" +7(351)700-00-95\n'
               'ГАУЗ "ГКБ № 11 г. Челябинск"  +7(351)214-29-29\n'
               'ГБУЗ ОКБ №2 +7(351)729-95-10\n'
               'ГБУЗ ОКБ №3 +7(351)239-29-18\n'
               'ЧУЗ «РЖД-Медицина» г. Челябинск» +7(351)701-62-19\n'
               'ООО «Полимедика» +7(351)240-99-77\n',
        "no": "Если Ваше состояние ухудшится, обязательно обратитесь к врачу "
              "или вызовете скорую медицинскую помощь (номера 112, 103)"
    }

    await call.message.answer(doctor_dict[call.data])
    # Here you would add the code to show an image if the answer is "no"
    if call.data == "no":
        await call.message.answer_photo(FSInputFile('image_if_no.jpg'),
                                        caption="Пожалуйста, не забывайте обращаться за медицинской помощью!")


# You would need to implement a way to track the number of user interactions
# This could be done using a database or a file-based system
