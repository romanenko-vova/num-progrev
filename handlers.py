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
    get_users_list,
    pre_buy_status,
    conversion_from_minuses_to_payment,
    conversion_from_start_to_minuses,
    overall_conversion_to_payment,
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

GET_DATE, GET_MINUSES, GET_MONEY_CODE, ADMIN_START = range(1, 5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Отправка сообщений с рассылкой", "Получить список юзеров"],["Калькулятор конверсии"]]
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    if update.effective_user.username == 'yur_numer':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Привет, {user_name}!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
            ),
        )
        return ADMIN_START
    else:
        await add_user(user_id, 0, user_name)
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
        return await get_date(update, context)


async def minuses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.effective_message.text
    status = 1
    await add_minuses(user_id, user_input, status)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Спасибо, {update.effective_user.full_name}!",
    )
    return await send_procents(update, context)


async def send_procents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dict_key = await calculate_30_procents(user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=send_pocents_message_dict[dict_key],
    )
    return await affirmative_message(update, context)


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
    else:
        return await affirmative_message(update, context)
    return await pre_buy_message(update, context)






async def pre_buy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Оплатить сейчас", callback_data="pay_now")]]
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

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    if query.data == "pay_now":
        await your_payment_function(update, context)




async def admin_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.text == "Отправка сообщений с рассылкой":
        message_text = update.effective_message.text
        users_list = await get_users_list()
        for user_id, _ in users_list:
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сообщение было отправлено всем пользователям",
        )
        return await start(update, context)
    elif update.effective_message.text == "Получить список юзеров":
        users_list = await get_users_list()
        last_40_users = users_list[-40:]  
        for user_id, username in last_40_users:
            message = f"имя пользователя: {username}, ID: {user_id}"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
                )
        remaining_users = users_list[:-40]  
        with open("users_list.txt", "w", encoding="utf-8") as file:
            for user_id, username in remaining_users:
                file.write(f"ID: {user_id}, Username: {username}\n")
        with open("users_list.txt", "rb") as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file)
        return await start(update, context)
    elif update.effective_message.text == "Калькулятор конверсии":
        first_rate = conversion_from_start_to_minuses()
        secon_rate = conversion_from_minuses_to_payment()
        final_rate = overall_conversion_to_payment()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Первый калькулятор: {first_rate}\nВторой калькулятор: {secon_rate}\nОбщий калькулятор: {final_rate}",
        )
        return start(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,     
            text="Пожалуйста, выберите один из вариантов",
        )
        return start(update, context)
    
