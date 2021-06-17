#!venv/bin/python

# Чтобы запустить бота через Long Polling - запустить этот файл

from tools.location import get_location

import logging
from decouple import config
from tools.throttling import rate_limit, ThrottlingMiddleware

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

bot = Bot(token=config('tgbot_token'))
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)


# Хэндлер на команду "/start"
@rate_limit('default')
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    logging.log(logging.INFO, f'user id:{message.from_user.id} send: {message.text}')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Где МКС?", "О боте"]
    keyboard.add(*buttons)
    await message.answer(
        f'<b>Привет, {message.from_user.first_name}!</b>\nЭтот бот подскажет тебе, где сейчас находится МКС '
        '(Международная Космическая Станция). Чтобы это случилось, '
        'нажми кнопку "Где МКС?", и бот отправит тебе местоположение станции.',
        parse_mode='HTML',
        reply_markup=keyboard
    )


# Хэндлер на команду "/test"
@rate_limit('default')
@dp.message_handler(commands='test')
async def cmd_test(message: types.Message):
    logging.log(logging.INFO, f'user id:{message.from_user.id} send: {message.text}')
    await message.reply('Это тестовое сообщение!')


# Хэндлер на команду "/location" или текст "Где МКС?"
@rate_limit('request')
@dp.message_handler(commands='location')
@dp.message_handler(Text(equals='Где МКС?'))
async def send_location(message: types.Message):
    logging.log(logging.INFO, f'user id:{message.from_user.id} send: {message.text}')
    lat, lng = await get_location()
    await bot.send_location(
        message.from_user.id,
        latitude=lat,
        longitude=lng
    )


# Хэндлер на команду "/about" или текст "О боте"
@rate_limit('default')
@dp.message_handler(commands='about')
@dp.message_handler(Text(equals='О боте'))
async def send_about(message: types.Message):
    logging.log(logging.INFO, f'user id:{message.from_user.id} send: {message.text}')
    await message.answer(
        'Если не знаешь, что такое МКС, посмотри '
        '<a href="https://nauka-prosto.ru/page/mezhdunarodnaya-kosmicheskaya-stantsiya/">это</a>\n'
        'Этот бот использует данные с сайта open-notify.org',
        parse_mode='HTML'
    )


# Установка команд
async def set_commands(dispatcher):
    commands = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="location", description="Где сейчас МКС?"),
        types.BotCommand(command="about", description="Справочная информация")
    ]
    await bot.set_my_commands(commands)


if __name__ == '__main__':
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
