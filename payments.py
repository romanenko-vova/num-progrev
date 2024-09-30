import uuid

from yookassa import Configuration, Payment

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
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def yookassa_payment(context: ContextTypes.DEFAULT_TYPE, price_str):
    Configuration.account_id = os.getenv('SHOP_ID')
    Configuration.secret_key = os.getenv('SECRET_KEY_YOUKASSA')
    if context.user_data.get('phone'):
        phone = context.user_data.get('phone')
    price = os.getenv(price_str)
    # print(phone)
    payment_process = Payment.create(
        {
            "amount": {"value": f"{price}", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/yur_numer_bot",
            },
            "capture": True,
            "description": 'Программа "Из минуса в плюс"',
            "receipt": {
                "customer": {"phone": f"{phone}"},
                "items": [
                    {
                        "description": 'Программа "Из минуса в плюс"',
                        "quantity": "1",
                        "amount": {"value": f"{price}", "currency": "RUB"},
                        "vat_code": "1",
                    },
                ],
            },
        },
        uuid.uuid4(),
    )

    payment_id = payment_process.id
    context.user_data["counter"] = 0
    context.user_data["payment"] = payment_process
    payment = Payment.find_one(payment_id)

    if payment.confirmation and payment.confirmation.type == "redirect":
        return payment.confirmation.confirmation_url


async def yookassa_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("check_message"):
        check_message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Проверяю оплату..."
        )
        context.user_data["check_message"] = check_message
    else:
        await asyncio.sleep(4)

    if not context.user_data.get("counter"):
        context.user_data["counter"] = 0

    counter = context.user_data["counter"]
    payment = context.user_data.get("payment")

    payment = Payment.find_one(payment.id)
    if payment:
        if counter < 6:
            if payment.status == "succeeded":
                from handlers import success_payment

                await context.bot.edit_message_text(
                    "Оплата прошла успешно ✅",
                    chat_id=check_message.chat.id,
                    message_id=check_message.id,
                )
                return await success_payment(update, context)
            else:
                counter += 1
                context.user_data["counter"] = counter
                return await yookassa_confirmation(update, context)
        else:
            import handlers

            return await handlers.chek_payment(update, context)
    else:
        return await yookassa_confirmation(update, context)
