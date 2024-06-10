import asyncio
import logging
import os

import dotenv
from texts import (
    send_pocents_message_dict,
    affirmative_message_dict,
    pre_buy_message_dict,
    arkans_dict
)
from creating_bd import (
    add_user,
    add_bithday_date,
    add_minuses,
    calculate_30_procents,
    add_arkans,
)
from triangle import (
    calc_money_code,
    create_triangle_image,
    make_arkans_flat_and_calc_unique,
)
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Создание объекта logger
logger = logging.getLogger(__name__)

GET_DATE, GET_MINUSES, GET_MONEY_CODE = range(1, 4)


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
        arkans, file_path = await create_triangle_image(user_id, user_input)
        with open(file_path, "rb") as file:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)
        arkans_flat, unique_arkans = await make_arkans_flat_and_calc_unique(arkans)
        arkans_flat = sorted(list(set(arkans_flat)))
        for arkan in arkans_flat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{arkans_dict[arkan]}",
            )
            asyncio.sleep(2)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите количество минусов",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
                parse_mod = ParseMode
            ),
        )
        return GET_MINUSES
    
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Извините, произошла ошибка."
        )
        return get_date(update, context)


async def minuses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.effective_message.text
    await add_minuses(user_id, user_input)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Спасибо, {update.effective_user.full_name}!",
    )
    await send_procents(update, context)


async def send_procents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dict_key = await calculate_30_procents(user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=send_pocents_message_dict[dict_key],
    )
    await affirmative_message(update, context)


async def affirmative_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Да"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=affirmative_message_dict[1]
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=affirmative_message_dict[0],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
            selective=True,
        ),
    )
    return GET_MONEY_CODE


async def get_money_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.text == "Да":
        pass
    return pre_buy_message(update, context)


async def pre_buy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Оплата через ЮКасса", url="ССЫЛКА_ДЛЯ_ОПЛАТЫ")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=pre_buy_message_dict[0],
    )
    asyncio.sleep(1)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=pre_buy_message_dict[1],
        reply_markup=reply_markup,
    )
