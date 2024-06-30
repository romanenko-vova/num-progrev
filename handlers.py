import asyncio
import logging
import os
import datetime
import dotenv
from texts import (
    hello_message,
    hello_message2,
    hello_message3,
    before_triangle_message,
    before_arkan_message,
    send_procents_message_dict,
    affirmative_message_dict,
    pre_buy_message_dict,
    arkans_dict,
    progrev_messages1,
    progrev_messages2
)

from payments import yookassa_payment

from creating_bd import (
    add_user,
    add_birthday_date,
    add_minuses,
    calculate_30_procents,
    add_arkans,
    get_users_list,
    get_payment_status,
    update_status,
    pre_buy_status,
    update_file_path,
    calculate_conversion,
    get_birthday_date,
    get_users_to_progrev,
    update_num_progrev,
    update_phone,
    update_conversation_status,
    load_conversation_status,
    update_file_path,
    get_file_path,
    get_arkans,
    update_flat_arkans,
    get_flat_arkans
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
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
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
    PREPREPARE_BUY_MESSAGE,
    PREREADY_BUY_MESSAGE,
    PREPARE_BUY_MESSAGE,
    GET_PHONE_NUMBER,
    CREATE_PAYMENT,
    BUY,
    ADMIN_START,
    GET_MAILING_MESSAGE,
    YOU_SURE,
    CONFIRMATION_PAYMENT,
    CHEK_PAYMENT,
) = range(1, 17)

admin_list = ["yur_numer", "romanenko_vova"]
TEST = False
if TEST:
    arkans_delay = 2
else:
    arkans_delay = 15


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

        context.job_queue.run_once(
            send_photo_job,
            datetime.timedelta(seconds=2),
            chat_id=update.effective_user.id,
            data={"i_path": "./imgs/message_progrev.jpeg", "text": hello_message2},
        )
        context.job_queue.run_once(
            send_text_job,
            datetime.timedelta(seconds=7),
            chat_id=update.effective_user.id,
            data={"text": hello_message3},
        )
        await update_conversation_status(update.effective_user.id, GET_DATE)
        return GET_DATE

async def load_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        text = 'Пожалуйста, нажмите на кнопку еще раз'
    elif update.effective_message.text:
        text = 'Пожалуйста, напишите сообщение еще раз'
        
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(text),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    
    status = await load_conversation_status(update.effective_user.id)
    return status

async def send_photo_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    i_path = job.data.get("i_path")
    text = job.data.get("text")

    with open(i_path, "rb") as image:
        await context.bot.send_photo(
            chat_id=job.chat_id,
            photo=image,
            caption=text_parse_mode(text),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def send_text_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    text = job.data.get("text")

    reply_markup = job.data.get("reply_markup")

    await context.bot.send_message(
        chat_id=job.chat_id,
        text=text_parse_mode(text),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )


async def send_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="*Пожалуйста\, введите дату рождения в формате дд\.мм\.гггг*",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await update_conversation_status(update.effective_user.id, GET_DATE)
    return GET_DATE


async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.effective_message.text
    user_id = update.effective_user.id

    arkans, file_path = await create_triangle_image(user_id, user_input)
    arkans_flat, unique_arkans = await make_arkans_flat_and_calc_unique(arkans)
    arkans_flat = sorted(list(set(arkans_flat)))

    context.user_data["birthday_date"] = update.effective_message.text
    context.user_data["arkanes"] = arkans_flat
    context.user_data["file_path"] = file_path
    
    await add_arkans(user_id, unique_arkans)
    await update_flat_arkans(user_id, arkans_flat)
    await add_birthday_date(user_id, user_input)
    await update_file_path(user_id, file_path)

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
    await update_conversation_status(update.effective_user.id, READY_TRIANGLE)
    return READY_TRIANGLE


async def send_triangle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("file_path"):
        file_path = context.user_data["file_path"]
    else:
        file_path = await get_file_path(update.effective_user.id)
    
    with open(file_path, "rb") as file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)

    inline_keyboard = [
        [InlineKeyboardButton("Получить расшифровку", callback_data="ready_arkanes")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    context.job_queue.run_once(
        send_text_job,
        datetime.timedelta(seconds=5),
        chat_id=update.effective_user.id,
        data={"text": before_arkan_message, "reply_markup": reply_markup},
    )

    status = 3
    await update_status(update.effective_user.id, status)
    await update_conversation_status(update.effective_user.id, READY_ARKANES)
    return READY_ARKANES


async def send_arkanes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("arkanes"):
        arkanes = context.user_data["arkanes"]
    else:
        arkanes = await get_flat_arkans(update.effective_user.id)
    
    seconds = 0
    for arkan in arkanes:
        context.job_queue.run_once(
            send_photo_job,
            datetime.timedelta(seconds=seconds),
            chat_id=update.effective_user.id,
            data={"text": arkans_dict[arkan], "i_path": f"./imgs/{arkan}.jpg"},
        )
        seconds += arkans_delay

    inline_keyboard = [
        [
            InlineKeyboardButton("0", callback_data="0min"),
            InlineKeyboardButton("1", callback_data="1min"),
            InlineKeyboardButton("2", callback_data="2min"),
            InlineKeyboardButton("3", callback_data="3min"),
            InlineKeyboardButton("4", callback_data="4min"),
            InlineKeyboardButton("5", callback_data="5min"),
            InlineKeyboardButton("6", callback_data="6min"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    
    context.job_queue.run_once(
        send_text_job,
        datetime.timedelta(seconds=seconds),
        chat_id=update.effective_user.id,
        data={"text": "Сколько у вас минусов и ГИПЕР?", "reply_markup": reply_markup},
    )

    status = 4
    await update_status(update.effective_user.id, status)
    await update_conversation_status(update.effective_user.id, GET_MINUSES)
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
    keyboard = [[InlineKeyboardButton("Да", callback_data="ready")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.job_queue.run_once(
        send_text_job,
        datetime.timedelta(seconds=5),
        chat_id=update.effective_user.id,
        data={"text": affirmative_message_dict[1], "reply_markup": reply_markup},
    )
    await update_conversation_status(update.effective_user.id, GET_MONEY_CODE)
    return GET_MONEY_CODE


async def get_money_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    birthday_date = context.user_data.get("birthday_date")
    if not birthday_date:
        birthday_date = await get_birthday_date(update.effective_user.id)

    money_code = calc_money_code(birthday_date)

    status = 6
    await update_status(update.effective_user.id, status)

    keyboard = [
        [InlineKeyboardButton("Как это сделать?", callback_data="ready_to_buy")]
    ]
    # await asyncio.sleep(1)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*Ваш денежный код\: __{money_code}__*\n\n"
        + text_parse_mode(pre_buy_message_dict[0]),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await update_conversation_status(update.effective_user.id, PREPREPARE_BUY_MESSAGE)
    return PREPREPARE_BUY_MESSAGE


async def preprepare_buy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "Из чего состоит эта расшифровка?", callback_data="prepre_buy_message"
            )
        ],
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(pre_buy_message_dict[1]),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await update_conversation_status(update.effective_user.id, PREREADY_BUY_MESSAGE)
    return PREREADY_BUY_MESSAGE


async def preready_buy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("ДА!", callback_data="ready_to_pay")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # await asyncio.sleep(1)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(pre_buy_message_dict[2]),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await update_conversation_status(update.effective_user.id, PREPARE_BUY_MESSAGE)
    return PREPARE_BUY_MESSAGE


async def pre_buy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    status = 7
    await update_status(update.effective_user.id, status)
    keyboard = [
        [
            InlineKeyboardButton(
                "Получить ссылку на оплату", callback_data="get_phone_number"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # await asyncio.sleep(1)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(pre_buy_message_dict[3]),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    context.job_queue.run_once(
        notify_to_pay,
        when=datetime.timedelta(minutes=30),
        chat_id=update.effective_user.id,
    )
    await update_conversation_status(update.effective_user.id, GET_PHONE_NUMBER)
    return GET_PHONE_NUMBER


async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[KeyboardButton("Отправить контакт", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="79998765432 или КНОПКА",
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, __*нажмите на кнопку снизу*__ или *напишите номер телефона в формате 79998765432*, чтобы __поделиться контактом для выставления чека__ ⬇️",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    
    await update_conversation_status(update.effective_user.id, CREATE_PAYMENT)
    return CREATE_PAYMENT

async def send_warning_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode("*Неверный формат номера. Пришлите номер в формате __79998765432__* или нажмите на кнопку снизу и поделитесь контактом."),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await update_conversation_status(update.effective_user.id, CREATE_PAYMENT)
    return CREATE_PAYMENT

async def create_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = 8
    await update_status(update.effective_user.id, status)
    if update.effective_message.contact:
        phone = f"{update.effective_message.contact.phone_number}"
    elif update.effective_message.text:
        phone = f"{update.effective_message.text}"
        
    context.user_data["phone"] = phone
    await update_phone(update.effective_user.id, phone)

    url = await yookassa_payment(context)
    keyboard = [
        [InlineKeyboardButton("Оплатить удобным способом", url=url)],
    ]
    
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Обработка...",
        reply_markup=ReplyKeyboardRemove(),
    )
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.id)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="*Ваша ссылка на оплату*\n\n_После оплаты обязательно вернитесь в бот для подтверждения_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    
    context.job_queue.run_once(confirmation_payment, datetime.timedelta(seconds=15), chat_id=update.effective_user.id)
    await update_conversation_status(update.effective_user.id, CONFIRMATION_PAYMENT)
    return CONFIRMATION_PAYMENT

async def confirmation_payment(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    keyboard = [
        [
            InlineKeyboardButton(
                "Подтвердить оплату", callback_data="confirmation_payment"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Нажмите кнопку для подтверждения оплаты",
        reply_markup=reply_markup,
    )
     

async def chek_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Обратиться в поддержку", url="https://t.me/yur_numer")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="К сожалению мы не смогли подтвердить оплату, вы можете написать в поддержку",
        reply_markup=reply_markup,
    )


async def notify_to_pay(context: ContextTypes.DEFAULT_TYPE, chat_id=None):
    if not chat_id:
        job = context.job
        chat_id = job.chat_id
    if await get_payment_status(chat_id) == 0:
        keyboard = [
            [
                InlineKeyboardButton(
                    "Получить ссылку на оплату", callback_data="get_phone_number"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=text_parse_mode(pre_buy_message_dict[4]),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def success_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Написать мне", url="https://t.me/yur_numer")]]
    status = 9
    await update_status(update.effective_user.id, status)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_parse_mode(
            "*Спасибо за оплату!*\n\nНапишите мне и я состалю для вас инструкцию по прохождению из - в +"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    # await context.bot.send_message(chat_id=492082141, text=f"@{update.effective_user.username} оплатил только что")
    context.user_data.clear()
    
    return ConversationHandler.END


async def send_progrev_message(context: ContextTypes.DEFAULT_TYPE):
    users_list = await get_users_to_progrev()
    # print(users_list)
    for user in users_list:
        if int(user[2]) < 7:
            await context.bot.send_message(
                chat_id=user[0],
                text=text_parse_mode(progrev_messages1[user[1]]),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            await update_num_progrev(user[0], user[1])
        else:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Получить ссылку на оплату", callback_data="get_phone_number"
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user[0],
                text=text_parse_mode(progrev_messages2[user[1]]),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup
            )
            await update_num_progrev(user[0], user[1])
            
        


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
            text="Сообщения успешно отправлены",
        )
    elif query.data == "not_sure":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отменено",
        )
    return await start(update, context)
