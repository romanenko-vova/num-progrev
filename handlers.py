import asyncio
import logging
import os

import dotenv
from texts import (
    hello_message,
    hello_message2,
    before_triangle_message,
    before_arkan_message,
    send_procents_message_dict,
    affirmative_message_dict,
    pre_buy_message_dict,
    arkans_dict,
)
from creating_bd import (
    add_user,
    add_bithday_date,
    add_minuses,
    calculate_30_procents,
    add_arkans,
    get_users_list,
    update_status,
    pre_buy_status,
    calculate_conversion,
    get_bithday_date,
)
from triangle import (
    calc_money_code,
    create_triangle_image,
    make_arkans_flat_and_calc_unique,
)
from states_list import states_list
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

from messages_proc import text_parse_mode

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Создание объекта logger
logger = logging.getLogger(__name__)

(
    GET_DATE,
    READY_TRIANGLE,
    READY_ARKANES,
    GET_MINUSES,
    GET_MONEY_CODE,
    PREPARE_BUY_MESSAGE,
    BUY,
    ADMIN_START,
    GET_MAILING_MESSAGE,
    YOU_SURE,
) = range(1, 11)

admin_list = ["yur_numer", "fromanenko_vova"]
TEST = True
if TEST:
    arkans_delay = 2
else:
    arkans_delay = 60


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Отправка сообщений с рассылкой", "Получить список пользователей"],
        ["Калькулятор конверсии"],
    ]
    user_id = update.effective_user.id
    username = update.effective_user.username
    if update.effective_user.username in admin_list:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы попали в панель администратора\nВыберите действие:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
            ),
        )
        return ADMIN_START
    else:
        status = 1
        await add_user(user_id, status, username)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text_parse_mode(hello_message),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await asyncio.sleep(1)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text_parse_mode(hello_message2),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return GET_DATE


async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    user_id = update.effective_user.id
    await add_bithday_date(user_id, user_input)
    context.user_data["birthday_date"] = update.effective_message.text

    arkans, file_path = await create_triangle_image(user_id, user_input)
    arkans_flat, unique_arkans = await make_arkans_flat_and_calc_unique(arkans)
    arkans_flat = sorted(list(set(arkans_flat)))

    context.user_data["arkanes"] = arkans_flat
    context.user_data["file_path"] = file_path
    await add_arkans(user_id, unique_arkans)

    inline_keyboard = [
        [
            InlineKeyboardButton(
                "Расcчитать мой треугольник", callback_data="ready_triangle"
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(before_triangle_message),
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    status = 2
    await update_status(update.effective_user.id, status)
    return READY_TRIANGLE


async def send_triangle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = context.user_data["file_path"]
    with open(file_path, "rb") as file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)

    inline_keyboard = [
        [InlineKeyboardButton("Готов считать", callback_data="ready_arkanes")]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(before_arkan_message),
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    status = 3
    await update_status(update.effective_user.id, status)

    return READY_ARKANES


async def send_arkanes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    inline_keyboard = [
        [
            InlineKeyboardButton("1", callback_data="1min"),
            InlineKeyboardButton("2", callback_data="2min"),
            InlineKeyboardButton("3", callback_data="3min"),
            InlineKeyboardButton("4", callback_data="4min"),
            InlineKeyboardButton("5", callback_data="5min"),
            InlineKeyboardButton("6", callback_data="6min"),
        ]
    ]

    arkanes = context.user_data["arkanes"]

    for arkan in arkanes:
        mess = text_parse_mode(arkans_dict[arkan])
        with open(f"./imgs/{arkan}.jpg", "rb") as file:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=file,
                caption=f"{mess}",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        await asyncio.sleep(arkans_delay)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Сколько у вас минусов и ГИПЕР?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
    )
    status = 4
    await update_status(update.effective_user.id, status)
    return GET_MINUSES


async def minuses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query

    await query.answer()
    num_minuses = int(query.data[0])
    status = 5
    await add_minuses(user_id, num_minuses, status)
    return await send_procents(update, context)


async def send_procents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dict_key = await calculate_30_procents(user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(send_procents_message_dict[dict_key]),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await asyncio.sleep(2)
    return await affirmative_message(update, context)


async def affirmative_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Да", callback_data="ready")]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=affirmative_message_dict[1]
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(affirmative_message_dict[0]),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard,
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return GET_MONEY_CODE


async def get_money_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    birthday_date = context.user_data.get("birthday_date")
    if not birthday_date:
        birthday_date = await get_bithday_date(update.effective_user.id)

    money_code = calc_money_code(birthday_date)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Ваш денежный код: {money_code}",
    )
    status = 6
    await update_status(update.effective_user.id, status)

    keyboard = [
        [InlineKeyboardButton("Как это сделать?", callback_data="ready_to_buy")]
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(pre_buy_message_dict[0]),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return PREPARE_BUY_MESSAGE


async def pre_buy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    status = 7
    await update_status(update.effective_user.id, status)

    keyboard = [[InlineKeyboardButton("Оплатить сейчас", callback_data="pay_now")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # await asyncio.sleep(1)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(pre_buy_message_dict[1]),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return BUY


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "pay_now":
        # context.job_queue.run_once()
        pass


async def confirmation_payment(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    keyboard = [
        [
            InlineKeyboardButton(
                "Подтвердить оплату", callback_data="confirmation_payment"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=pre_buy_message_dict[1],
        reply_markup=reply_markup,
    )


async def admin_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.text == "Отправка сообщений с рассылкой":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите сообщение, которое будет рассылаться:",
        )
        return GET_MAILING_MESSAGE
    elif update.effective_message.text == "Получить список пользователей":
        users_list = await get_users_list()
        users_list = users_list[::-1]
        message = ""
        count = 0
        for n, user_data in enumerate(users_list):
            message += f"{n+1}. @{user_data[1]}\n"
            count += 1
            if count == 80:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=message
                )
                count = 0
                message = ""
        if message:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=message
            )
        with open("users_list.txt", "w", encoding="utf-8") as file:
            for n, user_data in enumerate(users_list):
                file.write(f"https://t.me/{user_data[1]}\n")
        with open("users_list.txt", "rb") as file:
            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=file
            )
    elif update.effective_message.text == "Калькулятор конверсии":
        number_users = await calculate_conversion()
        message = f"{states_list[1]}"
        for n, number in enumerate(number_users[1:]):
            if number_users[n] > 0:
                conversion = round(number_users[n + 1] / number_users[n] * 100, 2)
            else:
                conversion = 0
            message += f"\n|\n|    {conversion}%\nv\n{states_list[n+2]}"

        total_conversion = round(number_users[-1] / number_users[0] * 100, 2)
        message += f"\n\nОбщая конверсия из зашедших в оплату — {total_conversion}%"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, выберите один из вариантов",
        )
    return await start(update, context)


async def get_mailing_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.effective_message.text
    message_text = text_parse_mode(message_text)
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="i_sure"),
            InlineKeyboardButton("Отменить", callback_data="not_sure"),
        ]
    ]
    context.user_data["mailing_message"] = message_text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы хотите отправить следующее сообщение:",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return YOU_SURE


async def get_confirmation_mailing_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    mailing_message = context.user_data["mailing_message"]
    if query.data == "i_sure":
        user_list = await get_users_list()
        for user in user_list:
            await context.bot.send_message(
                chat_id=user[2], text=mailing_message, parse_mode=ParseMode.MARKDOWN_V2
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Сообщения успешно отправлены',
        )
    elif query.data == "not_sure":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Отменено',
        )
    return await start(update, context)
