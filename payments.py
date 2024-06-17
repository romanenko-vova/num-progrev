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
Configuration.account_id = "349918"
Configuration.secret_key = "test_wwHRVzc1JTXUJhM5Wh9lV65VCFtc4iG2ryM0bKJ6SUw"
async def yookassa_payment(context: ContextTypes.DEFAULT_TYPE):
    payment_process = Payment.create({
        "amount": {
            "value": "1990.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/yur_numer_bot"
        },
        "capture": True,
        "description": "Заказ №1"
    }, uuid.uuid4())

    payment_id = payment_process.id
    context.user_data["counter"] = 0
    context.user_data["payment"] = payment_process
    payment = Payment.find_one(payment_id)

    if payment.confirmation and payment.confirmation.type == "redirect":
        return payment.confirmation.confirmation_url

async def yookassa_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = context.user_data.get("payment")
    counter = context.user_data["counter"]
    payment = Payment.find_one(payment.id)
    if payment:
        if counter < 6:
            if payment.status == "succeeded":
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Оплата прошла успешно"
                )
                context.user_data.clear()
            else:
                counter += 1
                context.user_data["counter"] = counter
                return await yookassa_confirmation(update, context)
        else:
            context.user_data.clear()
            import handlers
            return await handlers.chek_payment(update, context)
    else:
        return await yookassa_confirmation(update, context)