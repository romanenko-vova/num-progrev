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

Configuration.account_id = "349918"
Configuration.secret_key = "test_wwHRVzc1JTXUJhM5Wh9lV65VCFtc4iG2ryM0bKJ6SUw"


async def yookassa_payment(context: ContextTypes.DEFAULT_TYPE):
    payment_process = Payment.create(
        {
            "amount": {"value": "1990.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/yur_numer_bot",
            },
            "capture": True,
            "description": "Заказ №1",
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

    await asyncio.sleep(5)
    if not context.user_data['check_message']:
        check_message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Проверяю оплату..."
        )

    payment = context.user_data.get("payment")

    if not context.user_data.get("counter"):
        context.user_data["counter"] = 0
    counter = context.user_data["counter"]
    context.user_data['check_message'] = check_message
    payment = Payment.find_one(payment.id)
    if payment:
        if counter < 6:
            if payment.status == "succeeded":
                from handlers import success_payment
                await context.bot.edit_message_text('Оплата прошла успешно ✅', chat_id=check_message.chat.id, message_id=check_message.id)
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
