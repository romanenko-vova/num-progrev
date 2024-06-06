import asyncio
import logging
import os

import dotenv
from creating_bd import add_user, add_bithday_date, add_minuses
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Создание объекта logger
logger = logging.getLogger(__name__)

GET_DATE, GET_MINUSES = range(1, 3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    await add_user(user_id, 1, user_name)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {user_name}!",
    )
    asyncio.sleep(1)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите дату в формате ДД.ММ.ГГГГ",
    )
    return GET_DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1", "2", "3"], ["4", "5", "6"]]
    try:
        user_input = update.effective_message.text
        user_id = update.effective_user.id
        await add_bithday_date(user_id, user_input)
        file_path = "D:\Lessons python\num-progrev\image.png"
        with open(file_path, 'rb') as file:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите количество минусов",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
            )
        )
        return GET_MINUSES
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, произошла ошибка.")
        return get_date(update, context)

async def minuses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.effective_message.text
    await add_minuses(user_id, user_input)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Спасибо, {update.effective_user.full_name}!",
    )