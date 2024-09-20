import time
from aiogram import F, Router, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboard as kb

router = Router()


class Health(StatesGroup):
    doctor = State()
    name = State()
    age = State()
    blood_pressure1 = State()
    blood_pressure2 = State()
    illnesses = State()
    symptoms = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
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
async def health_age(message: Message, state: FSMContext):
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
    await message.answer('Ваше систолическое (верхнее) давление')


@router.message(Health.blood_pressure1)
async def health_pressure1(message: Message, state: FSMContext):
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
    await message.answer('Ваше диастолическое (нижнее) давление')


@router.message(Health.blood_pressure2)
async def health_answer(message: Message, state: FSMContext):
    try:
        if int(message.text) < 50:
            raise ValueError

        if len(message.text.split()) == 2 or int(message.text) >= 150:
            raise TypeError

    except ValueError:
        await message.answer("Давление не может быть меньше 50")
        return
    except TypeError:
        await message.answer("Давление введено не верно")
        return

    await state.update_data(blood_pressure2=message.text)
    data = await state.get_data()

    sys_pressure = int(data["blood_pressure1"])
    dia_pressure = int(data["blood_pressure2"])

    bp_category = categorize_blood_pressure(sys_pressure, dia_pressure)

    if bp_category != "АГ 3-й степени":
        await message.answer("Ставил ли Вам врач какой-то из следующих диагнозов?:", reply_markup=kb.illnesses_keyboard)

    else:
        # Если категория "АГ 3-й степени", сразу выводим результат и завершаем процесс
        await message.answer(
            "У вас обнаружена АГ 3-й степени. "
            "Сопровождается ли повышение давления головной болью, головокружением, потемнением в глазах, "
            "мельканием мушек, загрудинной болью или отсутствием мочи? (Да/Нет)")

        await state.set_state(Health.symptoms)
        return


@router.callback_query(lambda call: call.data in ["AG", "CHD", "CKD", "serdce", "nothing"])
async def illnesses(call: types.CallbackQuery, state: FSMContext):                                              # вывод результатов
    # Словарь для преобразования callback_data в текст
    illnesses_dict = {
        "AG": "Артериальная гипертензия",
        "CHD": "Сахарный диабет",
        "CKD": "Хроническая болезнь почек",
        "serdce": "Ишемическая болезнь сердца",
        "nothing": "Нет болезней"
    }

    # получаем выбранную болезнь
    selected_illnesses = illnesses_dict[call.data]

    # Обновляем состояние пользователя
    await state.update_data(illnesses=selected_illnesses)
    data = await state.get_data()

    # создаем визуально ожидание
    wait = await call.message.answer('Обрабатываю вашу информацию...⌛')
    time.sleep(2)
    wait2 = await call.message.answer("Еще совсем немного...")
    time.sleep(4)
    await wait.delete()
    await wait2.delete()

    health_status = await check_ur_health(call, state)
    if illnesses_dict == "nothing":
        await call.message.answer(f'Ваше имя: {data["name"]}\nВаш возраст: {data["age"]}\n'
                                       f'Ваше давление: {data["blood_pressure1"]}/{data["blood_pressure2"]}'
                                       '\n'
                                       f'Заключение:\n{health_status}\n')
        await state.clear()
    else:
        await call.message.answer(f'Ваше имя: {data["name"]}\nВаш возраст: {data["age"]}\n'
                              f'Ваше давление: {data["blood_pressure1"]}/{data["blood_pressure2"]}'
                              '\n'
                              f'Заключение:\n{health_status}\n'
                              '\n'
                              f'Хотели бы вы записаться на прием к врачу?', reply_markup=kb.SMD)
        await state.clear()


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
        warning = ("Ваш уровень артериального давления (АД) намного выше целевых значений. Рекомендуем Вам "
                   "регулярно изменять давление утром и вечером, а также вести дневник АД и частоты сердечных "
                   "сокращений.")

        conclusion = ("По описанным Вами жалобам наблюдаются симптомы гипертонического криза.\nЭто тяжелое "
                      "состояние, требующее вызова скорой медицинской помощи (тел. 103, 112).")

    else:
        warning = ("Ваш уровень артериального давления (АД) намного выше целевых значений. Рекомендуем Вам "
                   "регулярно изменять давление утром и вечером, а также вести дневник АД и частоты сердечных "
                   "сокращений. При ухудшении состояния и появлении "
                   "выше описанных симптомов вызовите скорую медицинскую помощь (тел. 103, 112).")

        conclusion = ("Требуется назначение или коррекция лечения. "
                      "Обратитесь за консультацией к лечащему врачу в ближайшее время"
                      "\n"
                      "Хотели бы вы записаться на прием к врачу?")

    # Возвращаем итоговое заключение
    return (f"Имя: {name}\nВозраст: {age}\n"
            f"Ваше давление: {sys_pressure}/{dia_pressure}\n"
            f"Заключение:\n{warning}"
            '\n'
            f"\n{conclusion}\n")


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
    await message.answer(health_status, reply_markup=kb.SMD)

    # Очищаем состояние после вывода данных
    await state.clear()


@router.callback_query(lambda call: call.data in ["yes", "no"])
async def smd(call: types.CallbackQuery, state: FSMContext):                                                    # список контактов поликлиник
    doctor_dict = {"yes": "вот список поликлиник в которые вы можете записаться на прием\n"
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
                   "no": ("Регулярное повышение артериального давления отрицательно влияет на ваше здоровье. "
                          "Рекомендуем обратиться за консультацией к специалисту.")
                   }

    selected_doc = doctor_dict[call.data]
    await state.update_data(doctor=selected_doc)
    data = await state.get_data()

    await call.message.answer(data["doctor"])


def categorize_blood_pressure(sys_pressure: int, dia_pressure: int) -> str:                                 # определаяем категорию давления
    # Определяем категорию на основании наибольшего давления
    if sys_pressure >= 180 or dia_pressure >= 110:
        return "АГ 3-й степени"
    elif 160 <= sys_pressure or 100 <= dia_pressure:
        return "артериальная гипертензия"
    elif 140 <= sys_pressure or 90 <= dia_pressure:
        return "артериальная гипертензия"
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


def get_blood_pressure_advice(category: str) -> str:                                                        # определяем категорию давления
    advice = {
        "Оптимальное": "Ваш давление в оптимальном диапазоне. Продолжайте вести здоровый образ жизни.",
        "Нормальное": "Ваш уровень артериального давления в норме.. Поддерживайте здоровый образ жизни.",
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


def check_blood_pressure(age: int, sys_pressure: int, dia_pressure: int):                                   # проверка уровня давления
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


async def process_symptoms(message: Message) -> str:
    symptoms = message.text.lower() == "да"
    if symptoms:
        return "У вас Артериальная гипертензия 3-й степени. Необходим вызов СМП 112, 103"
    else:
        return "У вас Артериальная гипертензия 3-й степени. Необходим вызов СМП 112, 103"


@router.callback_query(Health.illnesses, lambda call: call.data in ["AG", "CHD", "CKD", "serdce", "nothing"])
async def check_ur_health(call: types.CallbackQuery, state: FSMContext):                            # собераем информацию в одно сообщение
    data = await state.get_data()

    age = int(data["age"])
    sys_pressure = int(data["blood_pressure1"])
    dia_pressure = int(data["blood_pressure2"])
    bp_category = categorize_blood_pressure(sys_pressure, dia_pressure)
    illnesses_dict = {
        "AG": "Артериальная гипертензия",
        "CHD": "Сахарный диабет",
        "CKD": "Хроническая болезнь почек",
        "serdce": "Ишемическая болезнь сердца",
        "nothing": "Нет болезней"
    }

    # Определение целевых показателей для давления
    bp_check_result = check_blood_pressure(age, sys_pressure, dia_pressure)

    # Получаем рекомендации на основе категории давления
    category_advice = get_blood_pressure_advice(bp_category)

    selected_ill = illnesses_dict[call.data].lower()
    await state.update_data(illness=selected_ill)

    age_advice = ""
    if age < 18:
        age_advice = ("Данный бот предназначен для оценки уровня артериального давления для лиц старше 18 лет. "
                      "Если у вас есть жалобы то обратитесь к участковому педиатру.")
    elif age > 65:
        age_advice = "В вашем возрасте особенно важно регулярно контролировать давление и консультироваться с врачом."

    if bp_category == "Нормальное" or bp_category == "Оптимальное":

        recomend = ("Ваш уровень артериального давления в норме. "
                    "Продолжайте придерживаться принципов здорового образа жизни. "
                    "Если Вам назначены препараты для снижения артериального давления, "
                    "рекомендуем продолжить их прием.")
    else:
        recomend = ("Ваш уровень артериального давления (АД) выше целевых значений. "
                    "Рекомендуем Вам регулярно изменять давление утром и вечером, "
                    "а также вести дневник АД и частоты сердечных сокращений. "
                    "Требуется назначение или коррекция лечения. "
                    "Обратитесь за консультацией к лечащему врачу.")

    print(f"Рекомендуемый уровень артериального давления для Вас:"
          f"{bp_category}\n"
          f"{age_advice}\n"
          f"{recomend}")

    return (f"Рекомендуемый уровень артериального давления для Вас: {bp_category}\n"
            f"{age_advice}\n"
            f'{recomend}\n'
            f"{bp_check_result}\n"
            f"{category_advice}")

