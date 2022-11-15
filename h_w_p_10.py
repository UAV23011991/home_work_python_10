import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from info import candy_bot
import random

token = candy_bot.token
bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
class Form(StatesGroup):
    all_candys = 200
    max_candys = 28
    start = State()
    step = State()

@dp.message_handler(commands="start", state='*')
async def start_message(message: types.Message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1=types.KeyboardButton('game')
    item2=types.KeyboardButton('rules')
    item3=types.KeyboardButton('stop')
    markup.add(item1, item2, item3)
    await message.answer(f"""Привет, {message.from_user.full_name}! 
🍭🍭🍭 Мы будем играть в конфеты 🍭🍭🍭
Всего есть {Form.all_candys} конфет.
Каждый ход можно взять не более {Form.max_candys} конфет.
Кто заберет последнюю, тот и выйграл!
Если готов, нажми 'game'""",reply_markup=markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text=="rules", state='*')
async def game(message: types.Message):
    await message.answer(f'''Давай еще раз повторим:
1. Я играю против тебя.
2. У нас {Form.all_candys} конфет.
3. Ходим по очереди.
4. Брать можно максимум {Form.max_candys} конфет.
5. Кто забирает последнюю конфету, тот получает всё.''')
    
@dp.message_handler(lambda message: message.text=="stop", state='*')
async def game(message: types.Message):
    await message.answer('Я еще не придумал как реализвать эту ветку.')

@dp.message_handler(lambda message: message.text=="game", state=Form.start)
async def game(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['all_candys'] = 200
    await Form.step.set()
    await message.answer('Сколько конфет заберешь?')

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.step)
async def user_step(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if int(message.text) > Form.max_candys:
            await message.answer(f'Не больше {Form.max_candys}.')
            await Form.step.set()
        elif int(message.text) > data['all_candys']:
            await message.answer(f"Их ведь осталось {data['all_candys']}.")
            await Form.step.set()
        else:
            data['all_candys'] -= int(message.text)
            if data['all_candys'] == 0:
                await message.answer('Поздравляю!!!')
                await message.answer_photo('AgACAgIAAxkBAAIBt2ISVRsf4JprBKEf58UWxKpuiED_AALetjEbAAEskEhIxRW0VTy6RgEAAwIAA3gAAyME')
                await Form.start.set()
            else:
                await Form.step.set()
                await message.answer(f"Осталось {data['all_candys']} конфет.")
                bot_choice = data['all_candys'] % (Form.max_candys + 1)
                if bot_choice < 1:
                    bot_choice = random.randint(1, data['all_candys'])
            data['all_candys'] -= bot_choice
            if data['all_candys'] == 0:
                await message.answer('Я забираю  все конфеты)')
                await message.answer_photo('AgACAgIAAxkBAAIBt2ISVRsf4JprBKEf58UWxKpuiED_AALetjEbAAEskEhIxRW0VTy6RgEAAwIAA3gAAyME')
                await Form.start.set()
            else:
                await message.answer(f"""Мой ход.
{bot_choice}.
Осталось {data['all_candys']}.""")
    
    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)