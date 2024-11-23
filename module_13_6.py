import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

api = ''  #@BerellExpressLearningBot
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.add(button)
kb.add(button2)

kb3 = InlineKeyboardMarkup()
button5 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button6 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb3.add(button5)
kb3.add(button6)

kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
button3 = KeyboardButton(text='Мужчина')
button4 = KeyboardButton(text='Женщина')
kb2.add(button3)
kb2.add(button4)

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью', reply_markup=kb)

@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Нажми "Расчитать норму калорий"', reply_markup=kb3)


@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6.25 x рост (см) – 5 х возраст (г) (+ 5/-161) (в зависимости от пола)')
    await call.answer()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    sex = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    data = await state.update_data(age=float(message.text))
    await message.answer('Введите свой рост (в см целым числом или через точку)')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    data = await state.update_data(growth=float(message.text))
    await message.answer('Введите свой вес (в кг целым числом или через точку)')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_sex(message, state):
    data = await state.update_data(weight=float(message.text))
    await message.answer('Введите свой пол (Мужчина/Женщина)', reply_markup=kb2)
    await UserState.sex.set()


@dp.message_handler(state=UserState.sex)
async def send_calories(message, state):
    await state.update_data(sex=message.text.lower())
    data = await state.get_data()
    if data['sex'] == 'мужчина':
        await message.answer(
            f"Ваша норма калорий {10.0 * data['weight'] + 6.25 * data['growth'] - 5.0 * data['age'] + 5}")
    elif data['sex'] == 'женщина':
        await message.answer(
            f"Ваша норма калорий {10.0 * data['weight'] + 6.25 * data['growth'] - 5.0 * data['age'] - 161}")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
