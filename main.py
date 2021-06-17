#!venv/bin/python

# Чтобы запустить бота через Вебхуки - запустить этот файл

from tools.location import get_location
import const

import logging
from decouple import config
from tools.throttling import rate_limit, ThrottlingMiddleware

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.executor import start_webhook

bot = Bot(token=config('tgbot_token'))
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)


@rate_limit('default')
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Где МКС?", "О боте"]
    keyboard.add(*buttons)
    await message.answer(
        '<b>Привет!</b>\nЭтот бот подскажет тебе, где сейчас находится МКС '
        '(Международная Космическая Станция). Чтобы это случилось, '
        'нажми кнопку "Где МКС?", и бот отправит тебе местоположение станции.',
        parse_mode='HTML',
        reply_markup=keyboard
    )


@rate_limit('default')
@dp.message_handler(commands='test')
async def cmd_test(message: types.Message):
    await message.reply('Это тестовое сообщение!')


@rate_limit('request')
@dp.message_handler(commands='location')
@dp.message_handler(Text(equals='Где МКС?'))
async def send_location(message: types.Message):
    lat, lng = await get_location()
    await bot.send_location(
        message.from_user.id,
        latitude=lat,
        longitude=lng
    )


@rate_limit('default')
@dp.message_handler(commands='about')
@dp.message_handler(Text(equals='О боте'))
async def send_about(message: types.Message):
    await message.answer('Этот бот использует данные с сайта http://open-notify.org/')


async def startup_cmd(dispatcher):
    await bot.set_webhook(const.WEBHOOK_URL)
    commands = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="location", description="Где сейчас МКС?"),
        types.BotCommand(command="about", description="Справочная информация")
    ]
    await bot.set_my_commands(commands)


async def shutdown_cmd(dispatcher):
    await bot.delete_webhook()


if __name__ == '__main__':
    dp.middleware.setup(ThrottlingMiddleware())
    start_webhook(
        dp,
        skip_updates=True,
        on_startup=startup_cmd,
        on_shutdown=shutdown_cmd,
        webhook_path=const.WEBHOOK_PATH,
        host=const.WEBAPP_HOST,
        port=const.WEBAPP_PORT,
    )
